from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database.database import get_db
from database.models import Bus, BusLocation, Route
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class BusResponse(BaseModel):
    id: int
    bus_number: str
    route_id: int
    capacity: int
    is_active: bool
    created_at: str

class BusLocationResponse(BaseModel):
    bus_id: int
    latitude: float
    longitude: float
    speed: float
    direction: float
    timestamp: str

class BusWithLocationResponse(BaseModel):
    id: int
    bus_number: str
    route_id: int
    capacity: int
    is_active: bool
    current_location: Optional[BusLocationResponse]

@router.get("/", response_model=List[BusWithLocationResponse])
async def get_buses(db: Session = Depends(get_db)):
    """Get all active buses with their current locations"""
    buses = db.query(Bus).filter(Bus.is_active == True).all()
    
    from services.redis_service import redis_service
    
    bus_data = []
    for bus in buses:
        location = redis_service.get_bus_location(bus.id)
        
        current_location = None
        if location:
            current_location = BusLocationResponse(
                bus_id=location["bus_id"],
                latitude=location["latitude"],
                longitude=location["longitude"],
                speed=location["speed"],
                direction=location["direction"],
                timestamp=location["timestamp"]
            )
        
        bus_data.append(BusWithLocationResponse(
            id=bus.id,
            bus_number=bus.bus_number,
            route_id=bus.route_id,
            capacity=bus.capacity,
            is_active=bus.is_active,
            current_location=current_location
        ))
    
    return bus_data

@router.get("/{bus_id}", response_model=BusWithLocationResponse)
async def get_bus(bus_id: int, db: Session = Depends(get_db)):
    """Get a specific bus with its current location"""
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    from services.redis_service import redis_service
    location = redis_service.get_bus_location(bus.id)
    
    current_location = None
    if location:
        current_location = BusLocationResponse(
            bus_id=location["bus_id"],
            latitude=location["latitude"],
            longitude=location["longitude"],
            speed=location["speed"],
            direction=location["direction"],
            timestamp=location["timestamp"]
        )
    
    return BusWithLocationResponse(
        id=bus.id,
        bus_number=bus.bus_number,
        route_id=bus.route_id,
        capacity=bus.capacity,
        is_active=bus.is_active,
        current_location=current_location
    )

@router.get("/{bus_id}/location")
async def get_bus_location(bus_id: int, db: Session = Depends(get_db)):
    """Get current location of a specific bus"""
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    from services.redis_service import redis_service
    location = redis_service.get_bus_location(bus.id)
    
    if not location:
        raise HTTPException(status_code=404, detail="No location data available for this bus")
    
    return location

@router.get("/{bus_id}/history")
async def get_bus_location_history(bus_id: int, limit: int = 100, db: Session = Depends(get_db)):
    """Get location history for a specific bus"""
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    locations = db.query(BusLocation).filter(
        BusLocation.bus_id == bus_id
    ).order_by(BusLocation.timestamp.desc()).limit(limit).all()
    
    return [
        {
            "id": loc.id,
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "speed": loc.speed,
            "direction": loc.direction,
            "timestamp": loc.timestamp.isoformat()
        }
        for loc in locations
    ]

@router.post("/{bus_id}/location")
async def update_bus_location(
    bus_id: int,
    latitude: float,
    longitude: float,
    speed: float = 0.0,
    direction: float = 0.0,
    db: Session = Depends(get_db)
):
    """Update bus location (simulate GPS data)"""
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    # Store in database
    location = BusLocation(
        bus_id=bus_id,
        latitude=latitude,
        longitude=longitude,
        speed=speed,
        direction=direction,
        timestamp=datetime.utcnow()
    )
    
    db.add(location)
    db.commit()
    
    # Store in Redis for real-time access
    from services.redis_service import redis_service
    redis_service.set_bus_location(
        bus_id, latitude, longitude, speed, direction,
        datetime.utcnow().isoformat()
    )
    
    return {"message": "Location updated successfully", "location": location.id}
