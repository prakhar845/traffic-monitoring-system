#!/usr/bin/env python3
"""
Data Simulator Service
Generates realistic real-time data for the traffic monitoring system
"""

import asyncio
import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class DataSimulator:
    def __init__(self):
        self.routes = [
            {
                "id": 1,
                "route_number": "101",
                "route_name": "Downtown Express",
                "stops": [
                    {"id": 1, "name": "Downtown Central", "lat": 40.7128, "lng": -74.0060},
                    {"id": 4, "name": "City Hall", "lat": 40.7130, "lng": -74.0055},
                    {"id": 3, "name": "Airport Terminal", "lat": 40.6413, "lng": -73.7781}
                ]
            },
            {
                "id": 2,
                "route_number": "202",
                "route_name": "University Line",
                "stops": [
                    {"id": 2, "name": "University Gate", "lat": 40.7589, "lng": -73.9851},
                    {"id": 1, "name": "Downtown Central", "lat": 40.7128, "lng": -74.0060},
                    {"id": 5, "name": "Shopping Mall", "lat": 40.7505, "lng": -73.9934}
                ]
            },
            {
                "id": 3,
                "route_number": "303",
                "route_name": "Suburban Loop",
                "stops": [
                    {"id": 8, "name": "Suburban Center", "lat": 40.7831, "lng": -73.9712},
                    {"id": 2, "name": "University Gate", "lat": 40.7589, "lng": -73.9851},
                    {"id": 10, "name": "Hospital District", "lat": 40.7614, "lng": -73.9776}
                ]
            }
        ]
        
        self.buses = [
            {"id": 1, "bus_number": "BUS001", "route_id": 1, "current_stop_index": 0, "progress": 0.0},
            {"id": 2, "bus_number": "BUS002", "route_id": 1, "current_stop_index": 1, "progress": 0.3},
            {"id": 3, "bus_number": "BUS003", "route_id": 2, "current_stop_index": 0, "progress": 0.0},
            {"id": 4, "bus_number": "BUS004", "route_id": 2, "current_stop_index": 1, "progress": 0.5},
            {"id": 5, "bus_number": "BUS005", "route_id": 3, "current_stop_index": 0, "progress": 0.0},
            {"id": 6, "bus_number": "BUS006", "route_id": 3, "current_stop_index": 2, "progress": 0.8},
            {"id": 7, "bus_number": "BUS007", "route_id": 1, "current_stop_index": 2, "progress": 0.9}
        ]
        
        self.predictions = []
        self.traffic_conditions = {}
        
    def get_route_by_id(self, route_id: int) -> Optional[Dict]:
        """Get route by ID"""
        for route in self.routes:
            if route["id"] == route_id:
                return route
        return None
    
    def calculate_position(self, bus: Dict) -> Dict:
        """Calculate current position of a bus"""
        route = self.get_route_by_id(bus["route_id"])
        if not route or not route["stops"]:
            return {"latitude": 40.7128, "longitude": -74.0060, "speed": 0, "direction": 0}
        
        current_stop_index = bus["current_stop_index"]
        progress = bus["progress"]
        
        # Get current and next stops
        current_stop = route["stops"][current_stop_index]
        next_stop_index = (current_stop_index + 1) % len(route["stops"])
        next_stop = route["stops"][next_stop_index]
        
        # Calculate position between stops
        lat = current_stop["lat"] + (next_stop["lat"] - current_stop["lat"]) * progress
        lng = current_stop["lng"] + (next_stop["lng"] - current_stop["lng"]) * progress
        
        # Add some realistic movement variation
        lat += random.uniform(-0.001, 0.001)
        lng += random.uniform(-0.001, 0.001)
        
        # Calculate speed based on traffic conditions
        base_speed = random.uniform(15, 35)  # km/h
        traffic_factor = self.traffic_conditions.get(bus["route_id"], 1.0)
        speed = base_speed * traffic_factor
        
        # Calculate direction
        direction = math.degrees(math.atan2(
            next_stop["lng"] - current_stop["lng"],
            next_stop["lat"] - current_stop["lat"]
        ))
        
        return {
            "latitude": lat,
            "longitude": lng,
            "speed": speed,
            "direction": direction
        }
    
    def update_bus_positions(self) -> List[Dict]:
        """Update all bus positions"""
        updated_buses = []
        
        for bus in self.buses:
            # Move bus along route
            bus["progress"] += random.uniform(0.01, 0.05)  # 1-5% progress per update
            
            # If bus reaches next stop, move to next stop
            if bus["progress"] >= 1.0:
                bus["progress"] = 0.0
                bus["current_stop_index"] = (bus["current_stop_index"] + 1) % len(self.get_route_by_id(bus["route_id"])["stops"])
            
            # Calculate current position
            position = self.calculate_position(bus)
            
            # Create bus location data
            bus_location = {
                "id": bus["id"],
                "bus_number": bus["bus_number"],
                "route_id": bus["route_id"],
                "current_location": {
                    "latitude": position["latitude"],
                    "longitude": position["longitude"],
                    "speed": position["speed"],
                    "direction": position["direction"],
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            updated_buses.append(bus_location)
        
        return updated_buses
    
    def generate_predictions(self) -> List[Dict]:
        """Generate arrival predictions"""
        predictions = []
        
        for bus in self.buses:
            route = self.get_route_by_id(bus["route_id"])
            if not route or not route["stops"]:
                continue
            
            current_stop_index = bus["current_stop_index"]
            progress = bus["progress"]
            
            # Generate predictions for next few stops
            for i in range(min(3, len(route["stops"]))):
                stop_index = (current_stop_index + i) % len(route["stops"])
                stop = route["stops"][stop_index]
                
                # Calculate estimated arrival time
                if i == 0:
                    # Current stop - estimate based on progress
                    remaining_progress = 1.0 - progress
                    estimated_time = remaining_progress * 5  # 5 minutes per stop segment
                else:
                    # Future stops - estimate based on distance
                    estimated_time = i * 5 + random.uniform(-2, 2)
                
                arrival_time = datetime.utcnow() + timedelta(minutes=estimated_time)
                
                prediction = {
                    "id": len(predictions) + 1,
                    "bus_id": bus["id"],
                    "route_id": bus["route_id"],
                    "stop_id": stop["id"],
                    "predicted_arrival_time": arrival_time.isoformat(),
                    "confidence_score": random.uniform(0.7, 0.95),
                    "prediction_type": "ml_enhanced"
                }
                
                predictions.append(prediction)
        
        return predictions
    
    def update_traffic_conditions(self):
        """Update traffic conditions for all routes"""
        for route in self.routes:
            # Simulate varying traffic conditions
            traffic_level = random.choice(["light", "moderate", "heavy", "severe"])
            
            if traffic_level == "light":
                factor = random.uniform(0.8, 1.0)
            elif traffic_level == "moderate":
                factor = random.uniform(0.6, 0.8)
            elif traffic_level == "heavy":
                factor = random.uniform(0.4, 0.6)
            else:  # severe
                factor = random.uniform(0.2, 0.4)
            
            self.traffic_conditions[route["id"]] = factor
    
    def get_system_data(self) -> Dict:
        """Get complete system data"""
        # Update traffic conditions
        self.update_traffic_conditions()
        
        # Update bus positions
        bus_locations = self.update_bus_positions()
        
        # Generate predictions
        predictions = self.generate_predictions()
        
        return {
            "bus_locations": bus_locations,
            "predictions": predictions,
            "traffic_conditions": self.traffic_conditions,
            "timestamp": datetime.utcnow().isoformat(),
            "system_status": "operational"
        }

# Global simulator instance
data_simulator = DataSimulator()
