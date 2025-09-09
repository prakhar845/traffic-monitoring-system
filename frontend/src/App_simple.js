import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [routes, setRoutes] = useState([]);
  const [buses, setBuses] = useState([]);
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    // Load initial data
    loadRoutes();
    loadBuses();
    
    // Set up WebSocket connection
    const ws = new WebSocket('ws://localhost:8000/ws/live-updates');
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'update') {
          setBuses(data.bus_locations || []);
          setLastUpdate(new Date());
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, []);

  const loadRoutes = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/routes/');
      const data = await response.json();
      setRoutes(data);
    } catch (error) {
      console.error('Error loading routes:', error);
    }
  };

  const loadBuses = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/buses/');
      const data = await response.json();
      setBuses(data);
    } catch (error) {
      console.error('Error loading buses:', error);
    }
  };

  const handleRouteSelect = (route) => {
    setSelectedRoute(route);
  };

  return (
    <div className="app">
      <header className="header">
        <h1>🚌 Real-Time Public Transport Monitoring</h1>
        <p>Live bus tracking with arrival time predictions</p>
        <div className="connection-status">
          Status: {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
          {lastUpdate && (
            <span> | Last Update: {lastUpdate.toLocaleTimeString()}</span>
          )}
        </div>
      </header>
      
      <main className="main-content">
        <div className="sidebar">
          <div className="section">
            <h2>🚌 Routes</h2>
            {routes.map((route) => (
              <div
                key={route.id}
                className={`route-card ${selectedRoute?.id === route.id ? 'active' : ''}`}
                onClick={() => handleRouteSelect(route)}
              >
                <h3>{route.route_number}</h3>
                <p>{route.route_name}</p>
                <small>{route.description}</small>
              </div>
            ))}
          </div>

          <div className="section">
            <h2>🚌 Active Buses</h2>
            <div className="bus-list">
              {buses.map((bus) => (
                <div key={bus.id} className="bus-item">
                  <div className="bus-info">
                    <div className="bus-number">{bus.bus_number}</div>
                    <div className="bus-status">
                      Route: {bus.route_id}
                    </div>
                    {bus.current_location && (
                      <div className="bus-location">
                        Lat: {bus.current_location.latitude?.toFixed(4)}, 
                        Lng: {bus.current_location.longitude?.toFixed(4)}
                        <br />
                        Speed: {bus.current_location.speed?.toFixed(1)} km/h
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        <div className="map-container">
          <div className="map-placeholder">
            <h2>🗺️ Interactive Map</h2>
            <p>Map visualization would be displayed here</p>
            <p>Showing {buses.length} active buses</p>
            {selectedRoute && (
              <div>
                <h3>Selected Route: {selectedRoute.route_name}</h3>
                <p>Route {selectedRoute.route_number}</p>
                <p>Stops: {selectedRoute.stops?.length || 0}</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
