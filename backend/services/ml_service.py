import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import asyncio
from sqlalchemy.orm import Session
from database.models import BusLocation, Route, BusStop, RouteStop, Prediction, Bus, TrafficCondition
from services.redis_service import redis_service
import json
import math
import logging
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os

logger = logging.getLogger(__name__)

class MLPredictionService:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.model_path = "models/"
        self.prediction_horizon = 3600  # 1 hour
        self.update_interval = 300  # 5 minutes
        
        # Ensure models directory exists
        os.makedirs(self.model_path, exist_ok=True)
    
    async def initialize_models(self):
        """Initialize ML models for different routes"""
        try:
            # Load existing models or create new ones
            for route_id in [1, 2, 3, 4, 5]:  # Our 5 routes
                await self.load_or_create_model(route_id)
            
            logger.info("ML models initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing ML models: {e}")
    
    async def load_or_create_model(self, route_id: int):
        """Load existing model or create new one for a route"""
        model_file = f"{self.model_path}/route_{route_id}_model.pkl"
        scaler_file = f"{self.model_path}/route_{route_id}_scaler.pkl"
        
        try:
            if os.path.exists(model_file) and os.path.exists(scaler_file):
                # Load existing model
                self.models[route_id] = joblib.load(model_file)
                self.scalers[route_id] = joblib.load(scaler_file)
                logger.info(f"Loaded existing model for route {route_id}")
            else:
                # Create new model
                await self.create_model(route_id)
                logger.info(f"Created new model for route {route_id}")
        except Exception as e:
            logger.error(f"Error loading/creating model for route {route_id}: {e}")
    
    async def create_model(self, route_id: int):
        """Create a new ML model for a specific route"""
        try:
            # This would typically use historical data
            # For demo purposes, we'll create a simple model
            
            # Create a Random Forest model
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            
            # Create a scaler
            scaler = StandardScaler()
            
            # For demo, create some synthetic training data
            # In production, this would use real historical data
            X_train, y_train = self.generate_training_data(route_id)
            
            # Fit the scaler and model
            X_train_scaled = scaler.fit_transform(X_train)
            model.fit(X_train_scaled, y_train)
            
            # Save the model
            self.models[route_id] = model
            self.scalers[route_id] = scaler
            
            # Save to disk
            model_file = f"{self.model_path}/route_{route_id}_model.pkl"
            scaler_file = f"{self.model_path}/route_{route_id}_scaler.pkl"
            
            joblib.dump(model, model_file)
            joblib.dump(scaler, scaler_file)
            
            logger.info(f"Model created and saved for route {route_id}")
            
        except Exception as e:
            logger.error(f"Error creating model for route {route_id}: {e}")
    
    def generate_training_data(self, route_id: int) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic training data for demo purposes"""
        # In production, this would load real historical data
        np.random.seed(42)
        
        n_samples = 1000
        
        # Features: hour, day_of_week, weather, traffic_level, distance_to_stop
        X = np.column_stack([
            np.random.randint(0, 24, n_samples),  # hour
            np.random.randint(0, 7, n_samples),   # day_of_week
            np.random.randint(0, 4, n_samples),   # weather (0=sunny, 1=cloudy, 2=rainy, 3=stormy)
            np.random.randint(0, 4, n_samples),   # traffic_level (0=light, 1=moderate, 2=heavy, 3=severe)
            np.random.uniform(0, 10, n_samples)   # distance_to_stop (km)
        ])
        
        # Target: travel_time in minutes
        # Base time + traffic factor + weather factor + distance factor
        base_time = 5  # 5 minutes base
        traffic_factor = X[:, 3] * 2  # 0-6 minutes based on traffic
        weather_factor = X[:, 2] * 1.5  # 0-4.5 minutes based on weather
        distance_factor = X[:, 4] * 3  # 3 minutes per km
        
        y = base_time + traffic_factor + weather_factor + distance_factor
        y += np.random.normal(0, 1, n_samples)  # Add some noise
        
        return X, y
    
    async def predict_arrival_time(self, db: Session, route_id: int, bus_id: int, 
                                 stop_id: int) -> Optional[Dict]:
        """Predict arrival time using ML model"""
        try:
            if route_id not in self.models:
                await self.load_or_create_model(route_id)
            
            # Get current bus location
            current_location = redis_service.get_bus_location(bus_id)
            if not current_location:
                return None
            
            # Get route and stop information
            route = db.query(Route).filter(Route.id == route_id).first()
            stop = db.query(BusStop).filter(BusStop.id == stop_id).first()
            
            if not route or not stop:
                return None
            
            # Calculate distance to stop
            distance = self.calculate_distance(
                current_location["latitude"], current_location["longitude"],
                stop.latitude, stop.longitude
            )
            
            # Get current traffic condition
            traffic_condition = redis_service.get_traffic_condition(route_id)
            traffic_level = 1  # moderate by default
            if traffic_condition:
                traffic_map = {"light": 0, "moderate": 1, "heavy": 2, "severe": 3}
                traffic_level = traffic_map.get(traffic_condition.get("traffic_level", "moderate"), 1)
            
            # Prepare features
            current_time = datetime.utcnow()
            features = np.array([[
                current_time.hour,                    # hour
                current_time.weekday(),               # day_of_week
                0,                                    # weather (simplified)
                traffic_level,                        # traffic_level
                distance                              # distance_to_stop
            ]])
            
            # Make prediction
            model = self.models[route_id]
            scaler = self.scalers[route_id]
            
            features_scaled = scaler.transform(features)
            predicted_travel_time = model.predict(features_scaled)[0]
            
            # Calculate confidence based on model performance
            confidence = min(0.95, max(0.3, 1 - (distance / 10)))
            
            # Calculate arrival time
            arrival_time = current_time + timedelta(minutes=predicted_travel_time)
            
            return {
                "predicted_arrival_time": arrival_time.isoformat(),
                "confidence_score": confidence,
                "prediction_type": "ml_random_forest",
                "travel_time_minutes": predicted_travel_time,
                "distance_km": distance,
                "traffic_level": traffic_level
            }
            
        except Exception as e:
            logger.error(f"Error making ML prediction: {e}")
            return None
    
    async def update_predictions(self, db: Session):
        """Update ML predictions for all active buses"""
        try:
            active_buses = redis_service.get_all_active_buses()
            
            for bus_location in active_buses:
                bus_id = bus_location["bus_id"]
                
                # Get bus route
                bus = db.query(Bus).filter(Bus.id == bus_id).first()
                if not bus:
                    continue
                
                # Get upcoming stops for this route
                route_stops = db.query(RouteStop, BusStop).join(
                    BusStop, RouteStop.stop_id == BusStop.id
                ).filter(
                    RouteStop.route_id == bus.route_id
                ).order_by(RouteStop.sequence_order).all()
                
                # Make predictions for next 3 stops
                for i, (route_stop, stop) in enumerate(route_stops[:3]):
                    prediction = await self.predict_arrival_time(
                        db, bus.route_id, bus_id, stop.id
                    )
                    
                    if prediction:
                        # Store prediction in database
                        pred_record = Prediction(
                            route_id=bus.route_id,
                            stop_id=stop.id,
                            bus_id=bus_id,
                            predicted_arrival_time=datetime.fromisoformat(
                                prediction["predicted_arrival_time"]
                            ),
                            confidence_score=prediction["confidence_score"],
                            prediction_type=prediction["prediction_type"]
                        )
                        
                        db.add(pred_record)
            
            db.commit()
            logger.info("ML predictions updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating ML predictions: {e}")
            db.rollback()
    
    async def get_model_status(self) -> Dict:
        """Get status of all ML models"""
        status = {}
        for route_id, model in self.models.items():
            status[f"route_{route_id}"] = {
                "loaded": True,
                "type": type(model).__name__,
                "features": model.n_features_in_ if hasattr(model, 'n_features_in_') else "unknown"
            }
        
        return status
    
    async def retrain_model(self, route_id: int, db: Session):
        """Retrain model with new data"""
        try:
            # In production, this would use real historical data
            logger.info(f"Retraining model for route {route_id}")
            
            # Generate new training data (in production, load from database)
            X_train, y_train = self.generate_training_data(route_id)
            
            # Create new model
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            model.fit(X_train_scaled, y_train)
            
            # Update models
            self.models[route_id] = model
            self.scalers[route_id] = scaler
            
            # Save to disk
            model_file = f"{self.model_path}/route_{route_id}_model.pkl"
            scaler_file = f"{self.model_path}/route_{route_id}_scaler.pkl"
            
            joblib.dump(model, model_file)
            joblib.dump(scaler, scaler_file)
            
            logger.info(f"Model retrained successfully for route {route_id}")
            
        except Exception as e:
            logger.error(f"Error retraining model for route {route_id}: {e}")
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers"""
        R = 6371  # Earth's radius in kilometers
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2) * math.sin(dlon/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance
