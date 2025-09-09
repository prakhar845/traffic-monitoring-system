from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
from datetime import datetime

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()

@router.websocket("/live-updates")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle any incoming messages
            data = await websocket.receive_text()
            
            # Handle different message types
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                if message_type == "subscribe":
                    # Handle subscription to specific routes or stops
                    await handle_subscription(websocket, message)
                elif message_type == "ping":
                    # Respond to ping with pong
                    await manager.send_personal_message(
                        json.dumps({"type": "pong", "timestamp": datetime.utcnow().isoformat()}),
                        websocket
                    )
                    
            except json.JSONDecodeError:
                # Handle non-JSON messages
                pass
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def handle_subscription(websocket: WebSocket, message: dict):
    """Handle subscription to specific routes or stops"""
    subscription_type = message.get("subscription_type")
    
    if subscription_type == "route":
        route_id = message.get("route_id")
        # Send current data for the route
        await send_route_data(websocket, route_id)
    elif subscription_type == "stop":
        stop_id = message.get("stop_id")
        # Send current data for the stop
        await send_stop_data(websocket, stop_id)

async def send_route_data(websocket: WebSocket, route_id: int):
    """Send current data for a specific route"""
    try:
        from database.database import SessionLocal
        from services.redis_service import redis_service
        
        db = SessionLocal()
        try:
            # Get route buses
            from database.models import Bus
            buses = db.query(Bus).filter(Bus.route_id == route_id, Bus.is_active == True).all()
            
            bus_locations = []
            for bus in buses:
                location = redis_service.get_bus_location(bus.id)
                if location:
                    bus_locations.append({
                        "bus_id": bus.id,
                        "bus_number": bus.bus_number,
                        "location": location
                    })
            
            # Send route data
            route_data = {
                "type": "route_data",
                "route_id": route_id,
                "timestamp": datetime.utcnow().isoformat(),
                "bus_locations": bus_locations
            }
            
            await manager.send_personal_message(json.dumps(route_data), websocket)
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error sending route data: {e}")

async def send_stop_data(websocket: WebSocket, stop_id: int):
    """Send current data for a specific stop"""
    try:
        from database.database import SessionLocal
        
        db = SessionLocal()
        try:
            # Get predictions for the stop
            from database.models import Prediction, Bus, Route
            from datetime import datetime
            
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
                time_until_arrival = (pred.predicted_arrival_time - datetime.utcnow()).total_seconds() / 60
                
                prediction_data.append({
                    "bus_id": bus.id,
                    "bus_number": bus.bus_number,
                    "route_number": route.route_number,
                    "route_name": route.route_name,
                    "predicted_arrival_time": pred.predicted_arrival_time.isoformat(),
                    "minutes_until_arrival": round(time_until_arrival, 1),
                    "confidence_score": pred.confidence_score
                })
            
            # Send stop data
            stop_data = {
                "type": "stop_data",
                "stop_id": stop_id,
                "timestamp": datetime.utcnow().isoformat(),
                "predictions": prediction_data
            }
            
            await manager.send_personal_message(json.dumps(stop_data), websocket)
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error sending stop data: {e}")

# Export the manager for use in main.py
__all__ = ["manager"]
