from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Dict
import json
import asyncio
from datetime import datetime
import uvicorn
import os
from dotenv import load_dotenv

from database.database import get_db, init_database
from database.models import Route, Bus, BusStop, BusLocation, Prediction
from services.redis_service import redis_service
from services.prediction_service import prediction_service
from routers import routes, buses, stops, predictions
from routers.websocket_router import manager

load_dotenv()

app = FastAPI(
    title="Real-Time Public Transport Monitoring System",
    description="A system for monitoring public transport in real-time with arrival predictions",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes.router, prefix="/api/routes", tags=["routes"])
app.include_router(buses.router, prefix="/api/buses", tags=["buses"])
app.include_router(stops.router, prefix="/api/stops", tags=["stops"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])

# Use the manager from websocket_router

@app.on_event("startup")
async def startup_event():
    """Initialize database and start background tasks"""
    print("Starting up the application...")
    
    # Initialize database
    init_database()
    
    # Start background tasks
    asyncio.create_task(update_bus_locations())
    asyncio.create_task(update_predictions())
    asyncio.create_task(broadcast_updates())
    
    print("Application started successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("Shutting down the application...")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Real-Time Public Transport Monitoring System",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    redis_stats = redis_service.get_redis_stats()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "redis": redis_stats
    }

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

async def update_bus_locations():
    """Background task to simulate bus location updates"""
    while True:
        try:
            # Simulate GPS data updates
            active_buses = redis_service.get_all_active_buses()
            
            for bus_location in active_buses:
                bus_id = bus_location["bus_id"]
                
                # Simulate movement (in a real system, this would come from GPS devices)
                import random
                lat_offset = random.uniform(-0.001, 0.001)
                lon_offset = random.uniform(-0.001, 0.001)
                
                new_lat = bus_location["latitude"] + lat_offset
                new_lon = bus_location["longitude"] + lon_offset
                new_speed = random.uniform(20, 50)  # km/h
                new_direction = random.uniform(0, 360)
                
                # Update location in Redis
                redis_service.set_bus_location(
                    bus_id, new_lat, new_lon, new_speed, new_direction,
                    datetime.utcnow().isoformat()
                )
            
            await asyncio.sleep(5)  # Update every 5 seconds
            
        except Exception as e:
            print(f"Error updating bus locations: {e}")
            await asyncio.sleep(10)

async def update_predictions():
    """Background task to update predictions"""
    while True:
        try:
            # Update predictions every 5 minutes
            from database.database import SessionLocal
            db = SessionLocal()
            try:
                await prediction_service.update_all_predictions(db)
            finally:
                db.close()
            
            await asyncio.sleep(300)  # Update every 5 minutes
            
        except Exception as e:
            print(f"Error updating predictions: {e}")
            await asyncio.sleep(60)

async def broadcast_updates():
    """Background task to broadcast updates to connected clients"""
    while True:
        try:
            if manager.active_connections:
                # Get all active bus locations
                active_buses = redis_service.get_all_active_buses()
                
                # Get all predictions
                from database.database import SessionLocal
                db = SessionLocal()
                try:
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
                            "confidence_score": pred.confidence_score
                        })
                finally:
                    db.close()
                
                # Create update message
                update_message = {
                    "type": "update",
                    "timestamp": datetime.utcnow().isoformat(),
                    "bus_locations": active_buses,
                    "predictions": prediction_data
                }
                
                # Broadcast to all connected clients
                await manager.broadcast(json.dumps(update_message))
            
            await asyncio.sleep(10)  # Broadcast every 10 seconds
            
        except Exception as e:
            print(f"Error broadcasting updates: {e}")
            await asyncio.sleep(30)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=os.getenv("DEBUG", "True").lower() == "true"
    )
