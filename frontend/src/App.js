import React, { useState, useEffect } from 'react';
import MapComponent from './components/MapComponent';
import Sidebar from './components/Sidebar';
import WebSocketService from './services/WebSocketService';
import './App.css';

function App() {
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [busLocations, setBusLocations] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    // Initialize WebSocket connection
    WebSocketService.connect();
    
    // Set up event listeners
    WebSocketService.on('connect', () => {
      setIsConnected(true);
      console.log('Connected to WebSocket');
    });

    WebSocketService.on('disconnect', () => {
      setIsConnected(false);
      console.log('Disconnected from WebSocket');
    });

    WebSocketService.on('update', (data) => {
      setBusLocations(data.bus_locations || []);
      setPredictions(data.predictions || []);
      setLastUpdate(new Date());
    });

    // Cleanup on unmount
    return () => {
      WebSocketService.disconnect();
    };
  }, []);

  const handleRouteSelect = (route) => {
    setSelectedRoute(route);
    
    // Subscribe to route updates
    if (isConnected) {
      WebSocketService.send({
        type: 'subscribe',
        subscription_type: 'route',
        route_id: route.id
      });
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>🚌 Real-Time Public Transport Monitoring</h1>
        <p>Live bus tracking with arrival time predictions</p>
      </header>
      
      <main className="main-content">
        <Sidebar 
          selectedRoute={selectedRoute}
          onRouteSelect={handleRouteSelect}
          busLocations={busLocations}
          predictions={predictions}
          isConnected={isConnected}
          lastUpdate={lastUpdate}
        />
        
        <div className="map-container">
          <MapComponent 
            selectedRoute={selectedRoute}
            busLocations={busLocations}
            predictions={predictions}
          />
        </div>
      </main>
    </div>
  );
}

export default App;
