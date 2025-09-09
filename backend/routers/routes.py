from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database.database import get_db
from database.models import Route, RouteStop, BusStop
from pydantic import BaseModel

router = APIRouter()

class RouteResponse(BaseModel):
    id: int
    route_number: str
    route_name: str
    description: str
    is_active: bool
    created_at: str

class RouteWithStopsResponse(BaseModel):
    id: int
    route_number: str
    route_name: str
    description: str
    is_active: bool
    stops: List[dict]

@router.get("/", response_model=List[RouteResponse])
async def get_routes(db: Session = Depends(get_db)):
    """Get all active routes"""
    routes = db.query(Route).filter(Route.is_active == True).all()
    
    return [
        RouteResponse(
            id=route.id,
            route_number=route.route_number,
            route_name=route.route_name,
            description=route.description,
            is_active=route.is_active,
            created_at=route.created_at.isoformat()
        )
        for route in routes
    ]

@router.get("/{route_id}", response_model=RouteWithStopsResponse)
async def get_route(route_id: int, db: Session = Depends(get_db)):
    """Get a specific route with its stops"""
    route = db.query(Route).filter(Route.id == route_id).first()
    
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    # Get route stops with stop details
    route_stops = db.query(RouteStop, BusStop).join(
        BusStop, RouteStop.stop_id == BusStop.id
    ).filter(
        RouteStop.route_id == route_id
    ).order_by(RouteStop.sequence_order).all()
    
    stops = []
    for route_stop, stop in route_stops:
        stops.append({
            "stop_id": stop.id,
            "stop_name": stop.stop_name,
            "latitude": stop.latitude,
            "longitude": stop.longitude,
            "sequence_order": route_stop.sequence_order,
            "estimated_travel_time": route_stop.estimated_travel_time
        })
    
    return RouteWithStopsResponse(
        id=route.id,
        route_number=route.route_number,
        route_name=route.route_name,
        description=route.description,
        is_active=route.is_active,
        stops=stops
    )

@router.get("/{route_id}/buses")
async def get_route_buses(route_id: int, db: Session = Depends(get_db)):
    """Get all buses for a specific route"""
    route = db.query(Route).filter(Route.id == route_id).first()
    
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    buses = db.query(Bus).filter(
        Bus.route_id == route_id,
        Bus.is_active == True
    ).all()
    
    # Get real-time locations from Redis
    from services.redis_service import redis_service
    
    bus_data = []
    for bus in buses:
        location = redis_service.get_bus_location(bus.id)
        bus_data.append({
            "id": bus.id,
            "bus_number": bus.bus_number,
            "capacity": bus.capacity,
            "is_active": bus.is_active,
            "current_location": location
        })
    
    return {
        "route_id": route_id,
        "route_name": route.route_name,
        "buses": bus_data
    }
