import React, { useState, useEffect } from 'react';
import { MapPin, Bus, Clock, Wifi, WifiOff } from 'lucide-react';
import { routesAPI, predictionsAPI } from '../services/api';

const Sidebar = ({ 
  selectedRoute, 
  onRouteSelect, 
  busLocations, 
  predictions, 
  isConnected, 
  lastUpdate 
}) => {
  const [routes, setRoutes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadRoutes();
  }, []);

  const loadRoutes = async () => {
    try {
      setLoading(true);
      const response = await routesAPI.getAll();
      setRoutes(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load routes');
      console.error('Error loading routes:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };

  const getConnectionStatus = () => {
    if (isConnected) {
      return (
        <div className="connection-status">
          <Wifi size={16} />
          Connected
        </div>
      );
    } else {
      return (
        <div className="connection-status disconnected">
          <WifiOff size={16} />
          Disconnected
        </div>
      );
    }
  };

  if (loading) {
    return (
      <div className="sidebar">
        <div className="loading">Loading routes...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="sidebar">
        <div className="error">{error}</div>
        <button onClick={loadRoutes}>Retry</button>
      </div>
    );
  }

  return (
    <div className="sidebar">
      {getConnectionStatus()}
      
      {lastUpdate && (
        <div className="section">
          <h2>
            <Clock size={20} />
            Last Update
          </h2>
          <p>{formatTime(lastUpdate)}</p>
        </div>
      )}

      <div className="section">
        <h2>
          <Bus size={20} />
          Routes
        </h2>
        {routes.map((route) => (
          <div
            key={route.id}
            className={`route-card ${selectedRoute?.id === route.id ? 'active' : ''}`}
            onClick={() => onRouteSelect(route)}
          >
            <h3>{route.route_number}</h3>
            <p>{route.route_name}</p>
          </div>
        ))}
      </div>

      {selectedRoute && (
        <div className="section">
          <h2>
            <Bus size={20} />
            Active Buses
          </h2>
          <div className="bus-list">
            {busLocations
              .filter(location => {
                // Filter buses for selected route (you might need to add route_id to location data)
                return true; // For now, show all buses
              })
              .map((location) => (
                <div key={location.bus_id} className="bus-item">
                  <div className="status-indicator" />
                  <div className="bus-info">
                    <div className="bus-number">Bus {location.bus_id}</div>
                    <div className="bus-status">
                      Speed: {location.speed?.toFixed(1)} km/h
                    </div>
                    <div className="bus-location">
                      {location.latitude?.toFixed(4)}, {location.longitude?.toFixed(4)}
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      <div className="section">
        <h2>
          <Clock size={20} />
          Predictions
        </h2>
        {predictions.length > 0 ? (
          predictions.slice(0, 5).map((prediction) => (
            <div key={prediction.id} className="prediction-item">
              <div className="prediction-header">
                <div className="prediction-time">
                  {new Date(prediction.predicted_arrival_time).toLocaleTimeString()}
                </div>
                <div className="confidence-score">
                  {(prediction.confidence_score * 100).toFixed(0)}%
                </div>
              </div>
              <div className="prediction-details">
                Bus {prediction.bus_id} at Stop {prediction.stop_id}
              </div>
            </div>
          ))
        ) : (
          <p>No predictions available</p>
        )}
      </div>
    </div>
  );
};

export default Sidebar;
