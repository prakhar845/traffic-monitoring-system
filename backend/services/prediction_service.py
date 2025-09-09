import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import asyncio
from sqlalchemy.orm import Session
from database.models import BusLocation, Route, BusStop, RouteStop, Prediction, Bus
from services.redis_service import redis_service
import json
import math

class PredictionService:
    def __init__(self):
        self.prediction_horizon = 3600  # 1 hour in seconds
        self.update_interval = 300  # 5 minutes in seconds
        
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2) * math.sin(dlon/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance
    
    def get_route_segments(self, db: Session, route_id: int) -> List[Dict]:
        """Get route segments with stops and distances"""
        route_stops = db.query(RouteStop).filter(
            RouteStop.route_id == route_id
        ).order_by(RouteStop.sequence_order).all()
        
        segments = []
        for i, route_stop in enumerate(route_stops):
            stop = route_stop.stop
            segment = {
                "stop_id": stop.id,
                "stop_name": stop.stop_name,
                "latitude": stop.latitude,
                "longitude": stop.longitude,
                "sequence_order": route_stop.sequence_order,
                "estimated_travel_time": route_stop.estimated_travel_time
            }
            
            # Calculate distance to next stop
            if i < len(route_stops) - 1:
                next_stop = route_stops[i + 1].stop
                distance = self.calculate_distance(
                    stop.latitude, stop.longitude,
                    next_stop.latitude, next_stop.longitude
                )
                segment["distance_to_next"] = distance
            else:
                segment["distance_to_next"] = 0
            
            segments.append(segment)
        
        return segments
    
    def find_nearest_stop(self, bus_lat: float, bus_lon: float, 
                         route_segments: List[Dict]) -> Tuple[Optional[Dict], float]:
        """Find the nearest stop to the bus location"""
        min_distance = float('inf')
        nearest_stop = None
        
        for segment in route_segments:
            distance = self.calculate_distance(
                bus_lat, bus_lon,
                segment["latitude"], segment["longitude"]
            )
            
            if distance < min_distance:
                min_distance = distance
                nearest_stop = segment
        
        return nearest_stop, min_distance
    
    def predict_arrival_times_historical(self, db: Session, route_id: int, 
                                       bus_id: int, current_time: datetime) -> List[Dict]:
        """Predict arrival times using historical data"""
        # Get historical data for the last 7 days
        start_date = current_time - timedelta(days=7)
        
        historical_locations = db.query(BusLocation).filter(
            BusLocation.bus_id == bus_id,
            BusLocation.timestamp >= start_date,
            BusLocation.timestamp <= current_time
        ).order_by(BusLocation.timestamp).all()
        
        if not historical_locations:
            return []
        
        # Get route segments
        route_segments = self.get_route_segments(db, route_id)
        
        # Get current bus location from Redis
        current_location = redis_service.get_bus_location(bus_id)
        if not current_location:
            return []
        
        bus_lat = current_location["latitude"]
        bus_lon = current_location["longitude"]
        
        # Find nearest stop
        nearest_stop, distance_to_stop = self.find_nearest_stop(
            bus_lat, bus_lon, route_segments
        )
        
        if not nearest_stop:
            return []
        
        # Calculate average speed from historical data
        speeds = [loc.speed for loc in historical_locations if loc.speed > 0]
        avg_speed = np.mean(speeds) if speeds else 25  # Default 25 km/h
        
        # Adjust for traffic conditions
        traffic_condition = redis_service.get_traffic_condition(route_id)
        if traffic_condition:
            traffic_speed = traffic_condition.get("average_speed", avg_speed)
            avg_speed = (avg_speed + traffic_speed) / 2
        
        predictions = []
        
        # Predict arrival times for upcoming stops
        current_stop_index = nearest_stop["sequence_order"] - 1
        
        for i in range(current_stop_index, len(route_segments)):
            segment = route_segments[i]
            
            if i == current_stop_index:
                # Time to reach current nearest stop
                time_to_stop = (distance_to_stop / avg_speed) * 3600  # Convert to seconds
            else:
                # Time to reach subsequent stops
                time_to_stop = segment["estimated_travel_time"]
            
            predicted_arrival = current_time + timedelta(seconds=time_to_stop)
            
            # Calculate confidence based on data quality
            confidence = min(0.9, max(0.3, 1 - (distance_to_stop / 5)))  # Lower confidence for distant stops
            
            prediction = {
                "stop_id": segment["stop_id"],
                "stop_name": segment["stop_name"],
                "predicted_arrival_time": predicted_arrival.isoformat(),
                "confidence_score": confidence,
                "prediction_type": "historical",
                "estimated_travel_time": time_to_stop
            }
            
            predictions.append(prediction)
        
        return predictions
    
    def predict_arrival_times_simple(self, db: Session, route_id: int, 
                                   bus_id: int, current_time: datetime) -> List[Dict]:
        """Simple prediction based on route segments and current location"""
        # Get route segments
        route_segments = self.get_route_segments(db, route_id)
        
        # Get current bus location from Redis
        current_location = redis_service.get_bus_location(bus_id)
        if not current_location:
            return []
        
        bus_lat = current_location["latitude"]
        bus_lon = current_location["longitude"]
        bus_speed = current_location.get("speed", 25)  # Default 25 km/h
        
        # Find nearest stop
        nearest_stop, distance_to_stop = self.find_nearest_stop(
            bus_lat, bus_lon, route_segments
        )
        
        if not nearest_stop:
            return []
        
        # Adjust speed based on traffic
        traffic_condition = redis_service.get_traffic_condition(route_id)
        if traffic_condition:
            traffic_speed = traffic_condition.get("average_speed", bus_speed)
            bus_speed = (bus_speed + traffic_speed) / 2
        
        predictions = []
        current_stop_index = nearest_stop["sequence_order"] - 1
        
        for i in range(current_stop_index, len(route_segments)):
            segment = route_segments[i]
            
            if i == current_stop_index:
                # Time to reach current nearest stop
                time_to_stop = (distance_to_stop / bus_speed) * 3600  # Convert to seconds
            else:
                # Time to reach subsequent stops
                time_to_stop = segment["estimated_travel_time"]
            
            predicted_arrival = current_time + timedelta(seconds=time_to_stop)
            
            # Calculate confidence
            confidence = min(0.8, max(0.4, 1 - (distance_to_stop / 3)))
            
            prediction = {
                "stop_id": segment["stop_id"],
                "stop_name": segment["stop_name"],
                "predicted_arrival_time": predicted_arrival.isoformat(),
                "confidence_score": confidence,
                "prediction_type": "simple",
                "estimated_travel_time": time_to_stop
            }
            
            predictions.append(prediction)
        
        return predictions
    
    async def generate_predictions(self, db: Session, route_id: int, 
                                 bus_id: int) -> List[Dict]:
        """Generate predictions for a specific bus on a route"""
        current_time = datetime.utcnow()
        
        # Try to get cached predictions first
        cached_predictions = redis_service.get_prediction_cache(route_id, bus_id)
        if cached_predictions:
            return cached_predictions
        
        # Generate new predictions
        predictions = self.predict_arrival_times_simple(db, route_id, bus_id, current_time)
        
        # Cache the predictions
        if predictions:
            redis_service.set_prediction_cache(route_id, bus_id, predictions)
        
        return predictions
    
    async def update_all_predictions(self, db: Session):
        """Update predictions for all active buses"""
        active_buses = redis_service.get_all_active_buses()
        
        for bus_location in active_buses:
            bus_id = bus_location["bus_id"]
            
            # Get bus route from database
            bus = db.query(Bus).filter(Bus.id == bus_id).first()
            if not bus:
                continue
            
            # Generate predictions
            predictions = await self.generate_predictions(db, bus.route_id, bus_id)
            
            # Store predictions in database
            for prediction_data in predictions:
                prediction = Prediction(
                    route_id=bus.route_id,
                    stop_id=prediction_data["stop_id"],
                    bus_id=bus_id,
                    predicted_arrival_time=datetime.fromisoformat(
                        prediction_data["predicted_arrival_time"]
                    ),
                    confidence_score=prediction_data["confidence_score"],
                    prediction_type=prediction_data["prediction_type"]
                )
                
                db.add(prediction)
        
        db.commit()
    
    def get_predictions_for_stop(self, db: Session, stop_id: int, 
                               route_id: Optional[int] = None) -> List[Dict]:
        """Get predictions for a specific stop"""
        query = db.query(Prediction).filter(
            Prediction.stop_id == stop_id,
            Prediction.predicted_arrival_time > datetime.utcnow()
        )
        
        if route_id:
            query = query.filter(Prediction.route_id == route_id)
        
        predictions = query.order_by(Prediction.predicted_arrival_time).all()
        
        result = []
        for prediction in predictions:
            result.append({
                "bus_id": prediction.bus_id,
                "route_id": prediction.route_id,
                "stop_id": prediction.stop_id,
                "predicted_arrival_time": prediction.predicted_arrival_time.isoformat(),
                "confidence_score": prediction.confidence_score,
                "prediction_type": prediction.prediction_type,
                "created_at": prediction.created_at.isoformat()
            })
        
        return result

# Global prediction service instance
prediction_service = PredictionService()
