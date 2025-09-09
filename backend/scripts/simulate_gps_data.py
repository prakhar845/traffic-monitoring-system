#!/usr/bin/env python3
"""
GPS Data Simulation Script
Simulates realistic GPS data for buses on different routes
"""

import asyncio
import random
import time
import math
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import requests
import json

class GPSDataSimulator:
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.running = False
        
        # Route definitions with realistic coordinates
        self.routes = {
            1: {  # Downtown Express
                "name": "Downtown Express",
                "stops": [
                    {"name": "Downtown Central", "lat": 40.7128, "lng": -74.0060},
                    {"name": "City Hall", "lat": 40.7130, "lng": -74.0055},
                    {"name": "Airport Terminal", "lat": 40.6413, "lng": -73.7781}
                ],
                "buses": [1, 2]
            },
            2: {  # University Line
                "name": "University Line", 
                "stops": [
                    {"name": "University Gate", "lat": 40.7589, "lng": -73.9851},
                    {"name": "Downtown Central", "lat": 40.7128, "lng": -74.0060},
                    {"name": "Shopping Mall", "lat": 40.7505, "lng": -73.9934}
                ],
                "buses": [3, 4]
            },
            3: {  # Suburban Loop
                "name": "Suburban Loop",
                "stops": [
                    {"name": "Shopping Mall", "lat": 40.7505, "lng": -73.9934},
                    {"name": "University Gate", "lat": 40.7589, "lng": -73.9851},
                    {"name": "City Hall", "lat": 40.7130, "lng": -74.0055}
                ],
                "buses": [5]
            }
        }
        
        # Bus states
        self.bus_states = {}
        
    def calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points in kilometers"""
        R = 6371  # Earth's radius in kilometers
        
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlng/2) * math.sin(dlng/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    def interpolate_position(self, start: Dict, end: Dict, progress: float) -> Tuple[float, float]:
        """Interpolate position between two points"""
        lat = start["lat"] + (end["lat"] - start["lat"]) * progress
        lng = start["lng"] + (end["lng"] - start["lng"]) * progress
        return lat, lng
    
    def calculate_direction(self, start: Dict, end: Dict) -> float:
        """Calculate direction from start to end point"""
        dlat = end["lat"] - start["lat"]
        dlng = end["lng"] - start["lng"]
        
        # Convert to degrees
        direction = math.degrees(math.atan2(dlng, dlat))
        return (direction + 360) % 360
    
    def initialize_bus_state(self, bus_id: int, route_id: int):
        """Initialize bus state for simulation"""
        route = self.routes[route_id]
        stops = route["stops"]
        
        # Start at first stop
        start_stop = stops[0]
        end_stop = stops[1] if len(stops) > 1 else stops[0]
        
        self.bus_states[bus_id] = {
            "route_id": route_id,
            "current_stop_index": 0,
            "next_stop_index": 1,
            "progress": 0.0,  # Progress between current and next stop
            "speed": random.uniform(20, 40),  # km/h
            "direction": self.calculate_direction(start_stop, end_stop),
            "last_update": datetime.utcnow(),
            "is_at_stop": False,
            "stop_wait_time": 0
        }
    
    def update_bus_position(self, bus_id: int) -> Dict:
        """Update bus position based on current state"""
        if bus_id not in self.bus_states:
            return None
        
        state = self.bus_states[bus_id]
        route = self.routes[state["route_id"]]
        stops = route["stops"]
        
        current_stop = stops[state["current_stop_index"]]
        next_stop = stops[state["next_stop_index"]]
        
        # If at a stop, wait for some time
        if state["is_at_stop"]:
            state["stop_wait_time"] += 1
            if state["stop_wait_time"] >= 30:  # Wait 30 seconds at stop
                state["is_at_stop"] = False
                state["stop_wait_time"] = 0
                # Move to next stop
                state["current_stop_index"] = state["next_stop_index"]
                state["next_stop_index"] = (state["next_stop_index"] + 1) % len(stops)
                state["progress"] = 0.0
                state["direction"] = self.calculate_direction(current_stop, next_stop)
            else:
                # Stay at current stop
                return {
                    "bus_id": bus_id,
                    "latitude": current_stop["lat"],
                    "longitude": current_stop["lng"],
                    "speed": 0.0,
                    "direction": state["direction"],
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        # Move towards next stop
        distance = self.calculate_distance(
            current_stop["lat"], current_stop["lng"],
            next_stop["lat"], next_stop["lng"]
        )
        
        # Calculate movement based on speed (km/h to degrees per second)
        speed_kmh = state["speed"]
        speed_degrees_per_sec = speed_kmh / 111.32  # Rough conversion
        
        # Add some randomness to speed
        speed_variation = random.uniform(0.8, 1.2)
        actual_speed = speed_kmh * speed_variation
        
        # Update progress
        progress_increment = (speed_degrees_per_sec * speed_variation) / distance
        state["progress"] += progress_increment
        
        # Check if reached next stop
        if state["progress"] >= 1.0:
            state["progress"] = 1.0
            state["is_at_stop"] = True
            state["speed"] = random.uniform(20, 40)  # Randomize speed for next segment
            return {
                "bus_id": bus_id,
                "latitude": next_stop["lat"],
                "longitude": next_stop["lng"],
                "speed": 0.0,
                "direction": state["direction"],
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Interpolate position
        lat, lng = self.interpolate_position(current_stop, next_stop, state["progress"])
        
        # Add some GPS noise
        lat += random.uniform(-0.0001, 0.0001)
        lng += random.uniform(-0.0001, 0.0001)
        
        return {
            "bus_id": bus_id,
            "latitude": lat,
            "longitude": lng,
            "speed": actual_speed,
            "direction": state["direction"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def send_location_update(self, location_data: Dict):
        """Send location update to the API"""
        try:
            response = requests.post(
                f"{self.api_base_url}/api/buses/{location_data['bus_id']}/location",
                params={
                    "latitude": location_data["latitude"],
                    "longitude": location_data["longitude"],
                    "speed": location_data["speed"],
                    "direction": location_data["direction"]
                },
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✅ Updated location for bus {location_data['bus_id']}")
            else:
                print(f"❌ Failed to update bus {location_data['bus_id']}: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error sending update for bus {location_data['bus_id']}: {e}")
    
    async def simulate_route(self, route_id: int):
        """Simulate all buses on a route"""
        route = self.routes[route_id]
        
        for bus_id in route["buses"]:
            if bus_id not in self.bus_states:
                self.initialize_bus_state(bus_id, route_id)
            
            location_data = self.update_bus_position(bus_id)
            if location_data:
                await self.send_location_update(location_data)
    
    async def run_simulation(self):
        """Run the GPS data simulation"""
        print("🚌 Starting GPS Data Simulation...")
        print("Press Ctrl+C to stop")
        
        self.running = True
        
        try:
            while self.running:
                # Simulate all routes
                for route_id in self.routes.keys():
                    await self.simulate_route(route_id)
                
                # Wait before next update
                await asyncio.sleep(5)  # Update every 5 seconds
                
        except KeyboardInterrupt:
            print("\n🛑 Simulation stopped by user")
        except Exception as e:
            print(f"❌ Simulation error: {e}")
        finally:
            self.running = False
    
    def stop(self):
        """Stop the simulation"""
        self.running = False

async def main():
    """Main function"""
    simulator = GPSDataSimulator()
    
    # Check if API is available
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend API is available")
        else:
            print("❌ Backend API is not responding properly")
            return
    except requests.exceptions.RequestException:
        print("❌ Backend API is not available. Please start the backend server first.")
        return
    
    # Run simulation
    await simulator.run_simulation()

if __name__ == "__main__":
    asyncio.run(main())
