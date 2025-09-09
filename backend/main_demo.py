from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import json
import asyncio
from datetime import datetime
import uvicorn
import random
import math
from services.data_simulator import data_simulator

app = FastAPI(
    title="Real-Time Public Transport Monitoring System - DEMO",
    description="A demo system for monitoring public transport in real-time",
    version="1.0.0-demo"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
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

# Data simulator handles all demo data

@app.on_event("startup")
async def startup_event():
    """Initialize demo data and start background tasks"""
    print("Starting up the demo application...")
    
    # Start background tasks
    asyncio.create_task(update_bus_locations())
    asyncio.create_task(broadcast_updates())
    
    print("Demo application started successfully!")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Real-Time Public Transport Monitoring System - DEMO",
        "version": "1.0.0-demo",
        "status": "running",
        "note": "This is a demo version without database persistence"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "active_connections": len(manager.active_connections),
        "demo_mode": True
    }

@app.get("/api/routes/")
async def get_routes():
    """Get all routes"""
    return data_simulator.routes

@app.get("/api/routes/{route_id}")
async def get_route(route_id: int):
    """Get a specific route"""
    route = data_simulator.get_route_by_id(route_id)
    if not route:
        return {"error": "Route not found"}
    return route

@app.get("/api/buses/")
async def get_buses():
    """Get all buses with their current locations"""
    system_data = data_simulator.get_system_data()
    return system_data["bus_locations"]

@app.get("/api/buses/{bus_id}")
async def get_bus(bus_id: int):
    """Get a specific bus"""
    system_data = data_simulator.get_system_data()
    bus = next((b for b in system_data["bus_locations"] if b["id"] == bus_id), None)
    if not bus:
        return {"error": "Bus not found"}
    return bus

@app.get("/api/stops/")
async def get_stops():
    """Get all stops"""
    stops = []
    for route in data_simulator.routes:
        for stop in route["stops"]:
            if stop not in stops:
                stops.append(stop)
    return stops

@app.websocket("/ws/live-updates")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def update_bus_locations():
    """Background task to simulate bus movement"""
    while True:
        try:
            # Update bus positions using the data simulator
            data_simulator.update_bus_positions()
            await asyncio.sleep(5)  # Update every 5 seconds
            
        except Exception as e:
            print(f"Error updating bus locations: {e}")
            await asyncio.sleep(10)

async def broadcast_updates():
    """Background task to broadcast updates to connected clients"""
    while True:
        try:
            if manager.active_connections:
                # Get complete system data
                system_data = data_simulator.get_system_data()
                
                # Create update message
                update_message = {
                    "type": "update",
                    "timestamp": system_data["timestamp"],
                    "bus_locations": system_data["bus_locations"],
                    "predictions": system_data["predictions"],
                    "traffic_conditions": system_data["traffic_conditions"],
                    "system_status": system_data["system_status"]
                }
                
                # Broadcast to all connected clients
                await manager.broadcast(json.dumps(update_message))
            
            await asyncio.sleep(10)  # Broadcast every 10 seconds
            
        except Exception as e:
            print(f"Error broadcasting updates: {e}")
            await asyncio.sleep(30)

if __name__ == "__main__":
    uvicorn.run(
        "main_demo:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
