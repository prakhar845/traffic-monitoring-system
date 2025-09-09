import redis
import json
import asyncio
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class RedisService:
    def __init__(self):
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
        self.redis_password = os.getenv("REDIS_PASSWORD", "")
        
        self.redis_client = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            password=self.redis_password if self.redis_password else None,
            decode_responses=True
        )
        
        # Test connection
        try:
            self.redis_client.ping()
            print("Connected to Redis successfully")
        except Exception as e:
            print(f"Failed to connect to Redis: {e}")
    
    def set_bus_location(self, bus_id: int, latitude: float, longitude: float, 
                        speed: float, direction: float, timestamp: str) -> bool:
        """Store real-time bus location in Redis"""
        try:
            location_data = {
                "bus_id": bus_id,
                "latitude": latitude,
                "longitude": longitude,
                "speed": speed,
                "direction": direction,
                "timestamp": timestamp
            }
            
            key = f"bus_location:{bus_id}"
            self.redis_client.setex(key, 300, json.dumps(location_data))  # Expire in 5 minutes
            
            # Also store in a set for quick retrieval of all active buses
            self.redis_client.sadd("active_buses", bus_id)
            self.redis_client.expire("active_buses", 300)
            
            return True
        except Exception as e:
            print(f"Error setting bus location: {e}")
            return False
    
    def get_bus_location(self, bus_id: int) -> Optional[Dict]:
        """Get real-time bus location from Redis"""
        try:
            key = f"bus_location:{bus_id}"
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"Error getting bus location: {e}")
            return None
    
    def get_all_active_buses(self) -> List[Dict]:
        """Get locations of all active buses"""
        try:
            active_bus_ids = self.redis_client.smembers("active_buses")
            bus_locations = []
            
            for bus_id in active_bus_ids:
                location = self.get_bus_location(int(bus_id))
                if location:
                    bus_locations.append(location)
            
            return bus_locations
        except Exception as e:
            print(f"Error getting all active buses: {e}")
            return []
    
    def set_traffic_condition(self, route_id: int, traffic_level: str, 
                            average_speed: float, segment_coords: Dict) -> bool:
        """Store traffic condition for a route segment"""
        try:
            traffic_data = {
                "route_id": route_id,
                "traffic_level": traffic_level,
                "average_speed": average_speed,
                "segment_coords": segment_coords,
                "timestamp": str(asyncio.get_event_loop().time())
            }
            
            key = f"traffic_condition:{route_id}"
            self.redis_client.setex(key, 600, json.dumps(traffic_data))  # Expire in 10 minutes
            return True
        except Exception as e:
            print(f"Error setting traffic condition: {e}")
            return False
    
    def get_traffic_condition(self, route_id: int) -> Optional[Dict]:
        """Get traffic condition for a route"""
        try:
            key = f"traffic_condition:{route_id}"
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"Error getting traffic condition: {e}")
            return None
    
    def set_prediction_cache(self, route_id: int, stop_id: int, 
                           predictions: List[Dict]) -> bool:
        """Cache arrival time predictions"""
        try:
            key = f"predictions:{route_id}:{stop_id}"
            self.redis_client.setex(key, 60, json.dumps(predictions))  # Expire in 1 minute
            return True
        except Exception as e:
            print(f"Error setting prediction cache: {e}")
            return False
    
    def get_prediction_cache(self, route_id: int, stop_id: int) -> Optional[List[Dict]]:
        """Get cached arrival time predictions"""
        try:
            key = f"predictions:{route_id}:{stop_id}"
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"Error getting prediction cache: {e}")
            return None
    
    def clear_expired_data(self):
        """Clear expired data (this is handled automatically by Redis TTL)"""
        pass
    
    def get_redis_stats(self) -> Dict:
        """Get Redis statistics"""
        try:
            info = self.redis_client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0)
            }
        except Exception as e:
            print(f"Error getting Redis stats: {e}")
            return {}

# Global Redis service instance
redis_service = RedisService()
