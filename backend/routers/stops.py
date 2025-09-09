from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database.database import get_db
from database.models import BusStop, RouteStop, Route
from pydantic import BaseModel

router = APIRouter()

class StopResponse(BaseModel):
    id: int
    stop_id: str
    stop_name: str
    latitude: float
    longitude: float
    address: str
    is_active: bool
    created_at: str

class StopWithRoutesResponse(BaseModel):
    id: int
    stop_id: str
    stop_name: str
    latitude: float
    longitude: float
    address: str
    is_active: bool
    routes: List[dict]

@router.get("/", response_model=List[StopResponse])
async def get_stops(db: Session = Depends(get_db)):
    """Get all active bus stops"""
    stops = db.query(BusStop).filter(BusStop.is_active == True).all()
    
    return [
        StopResponse(
            id=stop.id,
            stop_id=stop.stop_id,
            stop_name=stop.stop_name,
            latitude=stop.latitude,
            longitude=stop.longitude,
            address=stop.address,
            is_active=stop.is_active,
            created_at=stop.created_at.isoformat()
        )
        for stop in stops
    ]

@router.get("/{stop_id}", response_model=StopWithRoutesResponse)
async def get_stop(stop_id: int, db: Session = Depends(get_db)):
    """Get a specific stop with its routes"""
    stop = db.query(BusStop).filter(BusStop.id == stop_id).first()
    
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")
    
    # Get routes that serve this stop
    route_stops = db.query(RouteStop, Route).join(
        Route, RouteStop.route_id == Route.id
    ).filter(
        RouteStop.stop_id == stop_id,
        Route.is_active == True
    ).all()
    
    routes = []
    for route_stop, route in route_stops:
        routes.append({
            "route_id": route.id,
            "route_number": route.route_number,
            "route_name": route.route_name,
            "sequence_order": route_stop.sequence_order,
            "estimated_travel_time": route_stop.estimated_travel_time
        })
    
    return StopWithRoutesResponse(
        id=stop.id,
        stop_id=stop.stop_id,
        stop_name=stop.stop_name,
        latitude=stop.latitude,
        longitude=stop.longitude,
        address=stop.address,
        is_active=stop.is_active,
        routes=routes
    )

@router.get("/nearby/{latitude}/{longitude}")
async def get_nearby_stops(
    latitude: float, 
    longitude: float, 
    radius: float = 1.0,  # km
    db: Session = Depends(get_db)
):
    """Get stops within a specified radius"""
    import math
    
    stops = db.query(BusStop).filter(BusStop.is_active == True).all()
    
    nearby_stops = []
    for stop in stops:
        # Calculate distance using Haversine formula
        R = 6371  # Earth's radius in kilometers
        
        dlat = math.radians(stop.latitude - latitude)
        dlon = math.radians(stop.longitude - longitude)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(latitude)) * math.cos(math.radians(stop.latitude)) * 
             math.sin(dlon/2) * math.sin(dlon/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        if distance <= radius:
            nearby_stops.append({
                "id": stop.id,
                "stop_id": stop.stop_id,
                "stop_name": stop.stop_name,
                "latitude": stop.latitude,
                "longitude": stop.longitude,
                "address": stop.address,
                "distance": round(distance, 2)
            })
    
    # Sort by distance
    nearby_stops.sort(key=lambda x: x["distance"])
    
    return {
        "center": {"latitude": latitude, "longitude": longitude},
        "radius": radius,
        "stops": nearby_stops
    }
