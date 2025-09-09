from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import json
import asyncio
from datetime import datetime, timedelta
import uvicorn
import os
from dotenv import load_dotenv
import logging
from contextlib import asynccontextmanager

# Import our modules
from database.database import get_db, init_database
from database.models import Route, Bus, BusStop, BusLocation, Prediction, TrafficCondition, User, SystemLog
from services.redis_service import redis_service
from services.prediction_service import prediction_service
from services.ml_service import MLPredictionService
from services.auth_service import AuthService
from routers import routes, buses, stops, predictions, auth, analytics
from routers.websocket_router import manager

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('traffic_monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Initialize services
ml_service = MLPredictionService()
auth_service = AuthService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Traffic Monitoring System...")
    
    # Initialize database
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    # Initialize ML models
    try:
        await ml_service.initialize_models()
        logger.info("ML models initialized successfully")
    except Exception as e:
        logger.error(f"ML model initialization failed: {e}")
    
    # Start background tasks
    asyncio.create_task(update_bus_locations())
    asyncio.create_task(update_predictions())
    asyncio.create_task(update_traffic_conditions())
    asyncio.create_task(broadcast_updates())
    asyncio.create_task(cleanup_old_data())
    
    logger.info("Traffic Monitoring System started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Traffic Monitoring System...")

app = FastAPI(
    title="Real-Time Public Transport Monitoring System - Production",
    description="Advanced system for monitoring public transport with ML predictions",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(routes.router, prefix="/api/routes", tags=["routes"])
app.include_router(buses.router, prefix="/api/buses", tags=["buses"])
app.include_router(stops.router, prefix="/api/stops", tags=["stops"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Real-Time Public Transport Monitoring System - Production",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Real-time GPS tracking",
            "ML-powered predictions",
            "Traffic condition monitoring",
            "User authentication",
            "Analytics dashboard",
            "WebSocket streaming"
        ]
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    try:
        # Check database
        db = next(get_db())
        db.execute("SELECT 1")
        
        # Check Redis
        redis_stats = redis_service.get_redis_stats()
        
        # Check ML models
        ml_status = await ml_service.get_model_status()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
            "redis": redis_stats,
            "ml_models": ml_status,
            "active_connections": len(manager.active_connections),
            "uptime": "running"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )

@app.websocket("/ws/live-updates")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Background tasks
async def update_bus_locations():
    """Enhanced bus location updates with real GPS simulation"""
    while True:
        try:
            db = next(get_db())
            buses = db.query(Bus).filter(Bus.is_active == True).all()
            
            for bus in buses:
                # Get current location from Redis or generate new one
                current_location = redis_service.get_bus_location(bus.id)
                
                if current_location:
                    # Simulate realistic movement
                    new_location = simulate_bus_movement(bus, current_location)
                    
                    # Store in database
                    location_record = BusLocation(
                        bus_id=bus.id,
                        latitude=new_location["latitude"],
                        longitude=new_location["longitude"],
                        speed=new_location["speed"],
                        direction=new_location["direction"],
                        timestamp=datetime.utcnow()
                    )
                    db.add(location_record)
                    
                    # Update Redis
                    redis_service.set_bus_location(
                        bus.id, new_location["latitude"], new_location["longitude"],
                        new_location["speed"], new_location["direction"],
                        datetime.utcnow().isoformat()
                    )
            
            db.commit()
            db.close()
            
            await asyncio.sleep(5)  # Update every 5 seconds
            
        except Exception as e:
            logger.error(f"Error updating bus locations: {e}")
            await asyncio.sleep(10)

async def update_predictions():
    """Update ML-powered predictions"""
    while True:
        try:
            db = next(get_db())
            await prediction_service.update_all_predictions(db)
            await ml_service.update_predictions(db)
            db.close()
            
            await asyncio.sleep(300)  # Update every 5 minutes
            
        except Exception as e:
            logger.error(f"Error updating predictions: {e}")
            await asyncio.sleep(60)

async def update_traffic_conditions():
    """Update traffic conditions based on bus speeds"""
    while True:
        try:
            db = next(get_db())
            routes = db.query(Route).filter(Route.is_active == True).all()
            
            for route in routes:
                # Analyze bus speeds to determine traffic conditions
                traffic_level = analyze_traffic_conditions(db, route.id)
                
                # Store traffic condition
                condition = TrafficCondition(
                    route_id=route.id,
                    segment_start_lat=0.0,  # Simplified for demo
                    segment_start_lng=0.0,
                    segment_end_lat=0.0,
                    segment_end_lng=0.0,
                    traffic_level=traffic_level["level"],
                    average_speed=traffic_level["speed"]
                )
                db.add(condition)
                
                # Update Redis
                redis_service.set_traffic_condition(
                    route.id, traffic_level["level"], traffic_level["speed"], {}
                )
            
            db.commit()
            db.close()
            
            await asyncio.sleep(60)  # Update every minute
            
        except Exception as e:
            logger.error(f"Error updating traffic conditions: {e}")
            await asyncio.sleep(60)

async def broadcast_updates():
    """Broadcast updates to connected clients"""
    while True:
        try:
            if manager.active_connections:
                # Get all active bus locations
                active_buses = redis_service.get_all_active_buses()
                
                # Get predictions
                db = next(get_db())
                predictions = db.query(Prediction).filter(
                    Prediction.predicted_arrival_time > datetime.utcnow()
                ).all()
                
                prediction_data = []
                for pred in predictions:
                    prediction_data.append({
                        "bus_id": pred.bus_id,
                        "route_id": pred.route_id,
                        "stop_id": pred.stop_id,
                        "predicted_arrival_time": pred.predicted_arrival_time.isoformat(),
                        "confidence_score": pred.confidence_score,
                        "prediction_type": pred.prediction_type
                    })
                
                db.close()
                
                # Create update message
                update_message = {
                    "type": "update",
                    "timestamp": datetime.utcnow().isoformat(),
                    "bus_locations": active_buses,
                    "predictions": prediction_data,
                    "system_status": "operational"
                }
                
                # Broadcast to all connected clients
                await manager.broadcast(json.dumps(update_message))
            
            await asyncio.sleep(10)  # Broadcast every 10 seconds
            
        except Exception as e:
            logger.error(f"Error broadcasting updates: {e}")
            await asyncio.sleep(30)

async def cleanup_old_data():
    """Clean up old data to maintain performance"""
    while True:
        try:
            db = next(get_db())
            
            # Clean up old location data (keep last 24 hours)
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            db.query(BusLocation).filter(
                BusLocation.timestamp < cutoff_time
            ).delete()
            
            # Clean up old predictions (keep last 2 hours)
            cutoff_time = datetime.utcnow() - timedelta(hours=2)
            db.query(Prediction).filter(
                Prediction.predicted_arrival_time < cutoff_time
            ).delete()
            
            # Clean up old traffic conditions (keep last 6 hours)
            cutoff_time = datetime.utcnow() - timedelta(hours=6)
            db.query(TrafficCondition).filter(
                TrafficCondition.timestamp < cutoff_time
            ).delete()
            
            db.commit()
            db.close()
            
            logger.info("Data cleanup completed")
            await asyncio.sleep(3600)  # Run every hour
            
        except Exception as e:
            logger.error(f"Error during data cleanup: {e}")
            await asyncio.sleep(3600)

def simulate_bus_movement(bus: Bus, current_location: Dict) -> Dict:
    """Simulate realistic bus movement"""
    import random
    import math
    
    # Get route stops
    route_stops = bus.route.stops if hasattr(bus, 'route') else []
    
    # Simulate movement towards next stop
    lat_offset = random.uniform(-0.001, 0.001)
    lon_offset = random.uniform(-0.001, 0.001)
    
    new_lat = current_location["latitude"] + lat_offset
    new_lon = current_location["longitude"] + lon_offset
    
    # Realistic speed based on traffic conditions
    base_speed = random.uniform(20, 40)
    traffic_factor = random.uniform(0.7, 1.3)
    new_speed = base_speed * traffic_factor
    
    # Calculate direction
    new_direction = random.uniform(0, 360)
    
    return {
        "latitude": new_lat,
        "longitude": new_lon,
        "speed": new_speed,
        "direction": new_direction
    }

def analyze_traffic_conditions(db: Session, route_id: int) -> Dict:
    """Analyze traffic conditions based on bus speeds"""
    # Get recent bus speeds for this route
    recent_locations = db.query(BusLocation).join(Bus).filter(
        Bus.route_id == route_id,
        BusLocation.timestamp > datetime.utcnow() - timedelta(minutes=10)
    ).all()
    
    if not recent_locations:
        return {"level": "moderate", "speed": 30.0}
    
    avg_speed = sum(loc.speed for loc in recent_locations) / len(recent_locations)
    
    if avg_speed > 35:
        level = "light"
    elif avg_speed > 25:
        level = "moderate"
    elif avg_speed > 15:
        level = "heavy"
    else:
        level = "severe"
    
    return {"level": level, "speed": avg_speed}

if __name__ == "__main__":
    uvicorn.run(
        "main_production:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=os.getenv("DEBUG", "False").lower() == "true",
        log_level="info"
    )
