from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database.database import get_db
from database.models import Prediction, Bus, Route, BusStop
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class PredictionResponse(BaseModel):
    id: int
    route_id: int
    stop_id: int
    bus_id: int
    predicted_arrival_time: str
    confidence_score: float
    prediction_type: str
    created_at: str

class StopPredictionResponse(BaseModel):
    stop_id: int
    stop_name: str
    predictions: List[dict]

@router.get("/", response_model=List[PredictionResponse])
async def get_predictions(
    route_id: Optional[int] = None,
    stop_id: Optional[int] = None,
    bus_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get predictions with optional filters"""
    query = db.query(Prediction).filter(
        Prediction.predicted_arrival_time > datetime.utcnow()
    )
    
    if route_id:
        query = query.filter(Prediction.route_id == route_id)
    if stop_id:
        query = query.filter(Prediction.stop_id == stop_id)
    if bus_id:
        query = query.filter(Prediction.bus_id == bus_id)
    
    predictions = query.order_by(Prediction.predicted_arrival_time).all()
    
    return [
        PredictionResponse(
            id=pred.id,
            route_id=pred.route_id,
            stop_id=pred.stop_id,
            bus_id=pred.bus_id,
            predicted_arrival_time=pred.predicted_arrival_time.isoformat(),
            confidence_score=pred.confidence_score,
            prediction_type=pred.prediction_type,
            created_at=pred.created_at.isoformat()
        )
        for pred in predictions
    ]

@router.get("/stop/{stop_id}", response_model=StopPredictionResponse)
async def get_predictions_for_stop(stop_id: int, db: Session = Depends(get_db)):
    """Get predictions for a specific stop"""
    stop = db.query(BusStop).filter(BusStop.id == stop_id).first()
    
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")
    
    # Get predictions for this stop
    predictions = db.query(Prediction, Bus, Route).join(
        Bus, Prediction.bus_id == Bus.id
    ).join(
        Route, Prediction.route_id == Route.id
    ).filter(
        Prediction.stop_id == stop_id,
        Prediction.predicted_arrival_time > datetime.utcnow()
    ).order_by(Prediction.predicted_arrival_time).all()
    
    prediction_data = []
    for pred, bus, route in predictions:
        # Calculate minutes until arrival
        time_until_arrival = (pred.predicted_arrival_time - datetime.utcnow()).total_seconds() / 60
        
        prediction_data.append({
            "prediction_id": pred.id,
            "bus_id": bus.id,
            "bus_number": bus.bus_number,
            "route_id": route.id,
            "route_number": route.route_number,
            "route_name": route.route_name,
            "predicted_arrival_time": pred.predicted_arrival_time.isoformat(),
            "minutes_until_arrival": round(time_until_arrival, 1),
            "confidence_score": pred.confidence_score,
            "prediction_type": pred.prediction_type
        })
    
    return StopPredictionResponse(
        stop_id=stop.id,
        stop_name=stop.stop_name,
        predictions=prediction_data
    )

@router.get("/route/{route_id}")
async def get_predictions_for_route(route_id: int, db: Session = Depends(get_db)):
    """Get predictions for all stops on a specific route"""
    route = db.query(Route).filter(Route.id == route_id).first()
    
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    # Get all stops for this route
    route_stops = db.query(BusStop, RouteStop).join(
        RouteStop, BusStop.id == RouteStop.stop_id
    ).filter(
        RouteStop.route_id == route_id
    ).order_by(RouteStop.sequence_order).all()
    
    route_predictions = []
    for stop, route_stop in route_stops:
        # Get predictions for this stop on this route
        predictions = db.query(Prediction, Bus).join(
            Bus, Prediction.bus_id == Bus.id
        ).filter(
            Prediction.route_id == route_id,
            Prediction.stop_id == stop.id,
            Prediction.predicted_arrival_time > datetime.utcnow()
        ).order_by(Prediction.predicted_arrival_time).all()
        
        stop_predictions = []
        for pred, bus in predictions:
            time_until_arrival = (pred.predicted_arrival_time - datetime.utcnow()).total_seconds() / 60
            
            stop_predictions.append({
                "bus_id": bus.id,
                "bus_number": bus.bus_number,
                "predicted_arrival_time": pred.predicted_arrival_time.isoformat(),
                "minutes_until_arrival": round(time_until_arrival, 1),
                "confidence_score": pred.confidence_score
            })
        
        route_predictions.append({
            "stop_id": stop.id,
            "stop_name": stop.stop_name,
            "latitude": stop.latitude,
            "longitude": stop.longitude,
            "sequence_order": route_stop.sequence_order,
            "predictions": stop_predictions
        })
    
    return {
        "route_id": route.id,
        "route_number": route.route_number,
        "route_name": route.route_name,
        "stops": route_predictions
    }

@router.post("/generate/{bus_id}")
async def generate_predictions_for_bus(bus_id: int, db: Session = Depends(get_db)):
    """Generate predictions for a specific bus"""
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    # Generate predictions using the prediction service
    from services.prediction_service import prediction_service
    
    predictions = await prediction_service.generate_predictions(db, bus.route_id, bus_id)
    
    return {
        "bus_id": bus_id,
        "route_id": bus.route_id,
        "predictions": predictions
    }
