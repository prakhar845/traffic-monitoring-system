from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from database.database import get_db
from database.models import BusLocation, Route, Bus, Prediction, TrafficCondition, SystemLog
from routers.auth import get_current_user, require_role
from database.models import User
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

router = APIRouter()

class AnalyticsResponse(BaseModel):
    total_routes: int
    total_buses: int
    total_stops: int
    active_buses: int
    total_predictions: int
    average_confidence: float

class RouteAnalytics(BaseModel):
    route_id: int
    route_name: str
    total_buses: int
    average_speed: float
    on_time_performance: float
    total_trips: int

class BusAnalytics(BaseModel):
    bus_id: int
    bus_number: str
    route_name: str
    total_distance: float
    average_speed: float
    total_trips: int
    last_seen: str

class TrafficAnalytics(BaseModel):
    route_id: int
    route_name: str
    current_traffic_level: str
    average_speed: float
    congestion_percentage: float

@router.get("/overview", response_model=AnalyticsResponse)
async def get_analytics_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get system analytics overview"""
    try:
        # Get basic counts
        total_routes = db.query(Route).filter(Route.is_active == True).count()
        total_buses = db.query(Bus).filter(Bus.is_active == True).count()
        total_stops = db.query(BusStop).filter(BusStop.is_active == True).count()
        
        # Get active buses (buses with recent location data)
        recent_time = datetime.utcnow() - timedelta(minutes=10)
        active_buses = db.query(BusLocation.bus_id).filter(
            BusLocation.timestamp > recent_time
        ).distinct().count()
        
        # Get prediction statistics
        total_predictions = db.query(Prediction).filter(
            Prediction.predicted_arrival_time > datetime.utcnow()
        ).count()
        
        avg_confidence = db.query(func.avg(Prediction.confidence_score)).filter(
            Prediction.predicted_arrival_time > datetime.utcnow()
        ).scalar() or 0.0
        
        return AnalyticsResponse(
            total_routes=total_routes,
            total_buses=total_buses,
            total_stops=total_stops,
            active_buses=active_buses,
            total_predictions=total_predictions,
            average_confidence=round(avg_confidence, 2)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/routes", response_model=List[RouteAnalytics])
async def get_route_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics for all routes"""
    try:
        routes = db.query(Route).filter(Route.is_active == True).all()
        analytics = []
        
        for route in routes:
            # Get buses for this route
            buses = db.query(Bus).filter(
                Bus.route_id == route.id,
                Bus.is_active == True
            ).all()
            
            # Get recent location data for average speed
            recent_time = datetime.utcnow() - timedelta(hours=1)
            avg_speed_result = db.query(func.avg(BusLocation.speed)).join(Bus).filter(
                Bus.route_id == route.id,
                BusLocation.timestamp > recent_time
            ).scalar()
            
            avg_speed = avg_speed_result or 0.0
            
            # Calculate on-time performance (simplified)
            on_time_predictions = db.query(Prediction).join(Bus).filter(
                Bus.route_id == route.id,
                Prediction.confidence_score > 0.7
            ).count()
            
            total_predictions = db.query(Prediction).join(Bus).filter(
                Bus.route_id == route.id
            ).count()
            
            on_time_performance = (on_time_predictions / total_predictions * 100) if total_predictions > 0 else 0
            
            analytics.append(RouteAnalytics(
                route_id=route.id,
                route_name=route.route_name,
                total_buses=len(buses),
                average_speed=round(avg_speed, 2),
                on_time_performance=round(on_time_performance, 2),
                total_trips=total_predictions
            ))
        
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/buses", response_model=List[BusAnalytics])
async def get_bus_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics for all buses"""
    try:
        buses = db.query(Bus).filter(Bus.is_active == True).all()
        analytics = []
        
        for bus in buses:
            # Get recent location data
            recent_time = datetime.utcnow() - timedelta(hours=24)
            locations = db.query(BusLocation).filter(
                BusLocation.bus_id == bus.id,
                BusLocation.timestamp > recent_time
            ).order_by(BusLocation.timestamp).all()
            
            # Calculate total distance (simplified)
            total_distance = 0.0
            if len(locations) > 1:
                for i in range(1, len(locations)):
                    prev_loc = locations[i-1]
                    curr_loc = locations[i]
                    distance = calculate_distance(
                        prev_loc.latitude, prev_loc.longitude,
                        curr_loc.latitude, curr_loc.longitude
                    )
                    total_distance += distance
            
            # Calculate average speed
            avg_speed = sum(loc.speed for loc in locations) / len(locations) if locations else 0.0
            
            # Get last seen time
            last_seen = locations[-1].timestamp if locations else bus.created_at
            
            analytics.append(BusAnalytics(
                bus_id=bus.id,
                bus_number=bus.bus_number,
                route_name=bus.route.route_name,
                total_distance=round(total_distance, 2),
                average_speed=round(avg_speed, 2),
                total_trips=len(locations),
                last_seen=last_seen.isoformat()
            ))
        
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/traffic", response_model=List[TrafficAnalytics])
async def get_traffic_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get traffic condition analytics"""
    try:
        routes = db.query(Route).filter(Route.is_active == True).all()
        analytics = []
        
        for route in routes:
            # Get latest traffic condition
            latest_condition = db.query(TrafficCondition).filter(
                TrafficCondition.route_id == route.id
            ).order_by(desc(TrafficCondition.timestamp)).first()
            
            if latest_condition:
                # Calculate congestion percentage based on traffic level
                congestion_map = {"light": 0, "moderate": 25, "heavy": 60, "severe": 90}
                congestion_percentage = congestion_map.get(latest_condition.traffic_level, 25)
                
                analytics.append(TrafficAnalytics(
                    route_id=route.id,
                    route_name=route.route_name,
                    current_traffic_level=latest_condition.traffic_level,
                    average_speed=latest_condition.average_speed,
                    congestion_percentage=congestion_percentage
                ))
        
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_system_performance(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Get system performance metrics (admin only)"""
    try:
        # Get prediction accuracy
        recent_time = datetime.utcnow() - timedelta(hours=24)
        high_confidence_predictions = db.query(Prediction).filter(
            Prediction.confidence_score > 0.8,
            Prediction.created_at > recent_time
        ).count()
        
        total_predictions = db.query(Prediction).filter(
            Prediction.created_at > recent_time
        ).count()
        
        accuracy = (high_confidence_predictions / total_predictions * 100) if total_predictions > 0 else 0
        
        # Get system logs
        error_logs = db.query(SystemLog).filter(
            SystemLog.level == "ERROR",
            SystemLog.timestamp > recent_time
        ).count()
        
        warning_logs = db.query(SystemLog).filter(
            SystemLog.level == "WARNING",
            SystemLog.timestamp > recent_time
        ).count()
        
        return {
            "prediction_accuracy": round(accuracy, 2),
            "total_predictions_24h": total_predictions,
            "high_confidence_predictions": high_confidence_predictions,
            "error_logs_24h": error_logs,
            "warning_logs_24h": warning_logs,
            "system_health": "healthy" if error_logs < 10 else "degraded"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/realtime")
async def get_realtime_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get real-time system metrics"""
    try:
        # Get current active buses
        recent_time = datetime.utcnow() - timedelta(minutes=5)
        active_buses = db.query(BusLocation.bus_id).filter(
            BusLocation.timestamp > recent_time
        ).distinct().count()
        
        # Get current predictions
        current_predictions = db.query(Prediction).filter(
            Prediction.predicted_arrival_time > datetime.utcnow()
        ).count()
        
        # Get average speed across all buses
        avg_speed = db.query(func.avg(BusLocation.speed)).filter(
            BusLocation.timestamp > recent_time
        ).scalar() or 0.0
        
        return {
            "active_buses": active_buses,
            "current_predictions": current_predictions,
            "average_speed": round(avg_speed, 2),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in kilometers"""
    import math
    
    R = 6371  # Earth's radius in kilometers
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat/2) * math.sin(dlat/2) + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon/2) * math.sin(dlon/2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance
