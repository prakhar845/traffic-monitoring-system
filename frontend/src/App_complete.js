import React, { useState, useEffect, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, CircleMarker } from 'react-leaflet';
import L from 'leaflet';
import { Bus, MapPin, Clock, User, BarChart3, Settings, LogOut, AlertCircle, RefreshCw } from 'lucide-react';
import './App.css';

// Fix for default markers in react-leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Custom bus icon
const createBusIcon = (color = '#667eea') => {
  return L.divIcon({
    className: 'custom-bus-icon',
    html: `
      <div style="
        background-color: ${color};
        width: 20px;
        height: 20px;
        border-radius: 50%;
        border: 2px solid white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 10px;
        font-weight: bold;
      ">
        🚌
      </div>
    `,
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  });
};

// Custom stop icon
const createStopIcon = (color = '#28a745') => {
  return L.divIcon({
    className: 'custom-stop-icon',
    html: `
      <div style="
        background-color: ${color};
        width: 16px;
        height: 16px;
        border-radius: 50%;
        border: 2px solid white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 8px;
      ">
        📍
      </div>
    `,
    iconSize: [16, 16],
    iconAnchor: [8, 8],
  });
};

function App() {
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [busLocations, setBusLocations] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [analytics, setAnalytics] = useState(null);
  const [ws, setWs] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [retryCount, setRetryCount] = useState(0);

  // Authentication
  const [loginForm, setLoginForm] = useState({ username: '', password: '' });
  const [showLogin, setShowLogin] = useState(true);

  // Error handling
  const handleError = useCallback((error, context = '') => {
    console.error(`Error in ${context}:`, error);
    setError(`${context}: ${error.message || error}`);
    
    // Auto-clear error after 5 seconds
    setTimeout(() => setError(null), 5000);
  }, []);

  // Retry mechanism
  const retry = useCallback(() => {
    setRetryCount(prev => prev + 1);
    setError(null);
    loadInitialData();
    connectWebSocket();
  }, []);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('access_token');
    if (token) {
      fetchUserInfo(token);
    } else {
      setShowLogin(true);
      setIsLoading(false);
    }
  }, []);

  const fetchUserInfo = async (token) => {
    try {
      const response = await fetch('http://localhost:8000/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        setIsAuthenticated(true);
        setShowLogin(false);
        loadInitialData();
        connectWebSocket();
      } else {
        localStorage.removeItem('access_token');
        setShowLogin(true);
      }
    } catch (error) {
      handleError(error, 'Fetching user info');
      setShowLogin(true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(loginForm),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access_token);
        setUser(data);
        setIsAuthenticated(true);
        setShowLogin(false);
        loadInitialData();
        connectWebSocket();
      } else {
        const errorData = await response.json();
        handleError(new Error(errorData.detail || 'Login failed'), 'Login');
      }
    } catch (error) {
      handleError(error, 'Login');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
    setIsAuthenticated(false);
    setShowLogin(true);
    if (ws) {
      ws.close();
    }
  };

  const loadInitialData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const headers = {
        'Authorization': `Bearer ${token}`
      };

      // Load routes
      const routesResponse = await fetch('http://localhost:8000/api/routes/', { headers });
      if (!routesResponse.ok) throw new Error('Failed to load routes');
      const routesData = await routesResponse.json();
      setRoutes(routesData);

      // Load buses
      const busesResponse = await fetch('http://localhost:8000/api/buses/', { headers });
      if (!busesResponse.ok) throw new Error('Failed to load buses');
      const busesData = await busesResponse.json();
      setBusLocations(busesData);

      // Load analytics if user has permission
      if (user?.role === 'admin' || user?.role === 'operator') {
        loadAnalytics();
      }
    } catch (error) {
      handleError(error, 'Loading initial data');
    }
  };

  const loadAnalytics = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/analytics/overview', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const analyticsData = await response.json();
        setAnalytics(analyticsData);
      }
    } catch (error) {
      handleError(error, 'Loading analytics');
    }
  };

  const connectWebSocket = useCallback(() => {
    try {
      const websocket = new WebSocket('ws://localhost:8000/ws/live-updates');
      
      websocket.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setError(null);
        setRetryCount(0);
      };

      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'update') {
            setBusLocations(data.bus_locations || []);
            setPredictions(data.predictions || []);
            setLastUpdate(new Date());
          }
        } catch (error) {
          handleError(error, 'Parsing WebSocket message');
        }
      };

      websocket.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        // Try to reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };

      websocket.onerror = (error) => {
        handleError(error, 'WebSocket connection');
        setIsConnected(false);
      };

      setWs(websocket);
    } catch (error) {
      handleError(error, 'WebSocket connection');
    }
  }, [handleError]);

  const handleRouteSelect = (route) => {
    setSelectedRoute(route);
  };

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner">
          <RefreshCw className="spinning" />
          <p>Loading system...</p>
        </div>
      </div>
    );
  }

  if (showLogin) {
    return (
      <div className="login-container">
        <div className="login-form">
          <h1>🚌 Traffic Monitoring System</h1>
          <h2>Login</h2>
          {error && (
            <div className="error-message">
              <AlertCircle size={16} />
              {error}
            </div>
          )}
          <form onSubmit={handleLogin}>
            <input
              type="text"
              placeholder="Username"
              value={loginForm.username}
              onChange={(e) => setLoginForm({...loginForm, username: e.target.value})}
              required
            />
            <input
              type="password"
              placeholder="Password"
              value={loginForm.password}
              onChange={(e) => setLoginForm({...loginForm, password: e.target.value})}
              required
            />
            <button type="submit">Login</button>
          </form>
          <p>Default: admin / admin123</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      {error && (
        <div className="error-banner">
          <AlertCircle size={16} />
          <span>{error}</span>
          <button onClick={retry} className="retry-btn">
            <RefreshCw size={16} />
            Retry
          </button>
        </div>
      )}
      
      <header className="header">
        <div className="header-left">
          <h1>🚌 Real-Time Public Transport Monitoring</h1>
          <p>Complete system with ML predictions and analytics</p>
        </div>
        <div className="header-right">
          <div className="connection-status">
            {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
          </div>
          <div className="user-info">
            <User size={16} />
            {user?.username} ({user?.role})
          </div>
          <button onClick={() => setShowAnalytics(!showAnalytics)} className="analytics-btn">
            <BarChart3 size={16} />
            Analytics
          </button>
          <button onClick={handleLogout} className="logout-btn">
            <LogOut size={16} />
            Logout
          </button>
        </div>
      </header>
      
      <main className="main-content">
        <div className="sidebar">
          <div className="section">
            <h2>
              <Bus size={20} />
              Routes
            </h2>
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
            <h2>
              <Bus size={20} />
              Active Buses
            </h2>
            <div className="bus-list">
              {busLocations.map((bus) => (
                <div key={bus.id} className="bus-item">
                  <div className="status-indicator" />
                  <div className="bus-info">
                    <div className="bus-number">{bus.bus_number}</div>
                    <div className="bus-status">Route: {bus.route_id}</div>
                    {bus.current_location && (
                      <div className="bus-location">
                        Speed: {bus.current_location.speed?.toFixed(1)} km/h
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {showAnalytics && analytics && (
            <div className="section">
              <h2>
                <BarChart3 size={20} />
                Analytics
              </h2>
              <div className="analytics-card">
                <div className="metric">
                  <span className="metric-label">Total Routes:</span>
                  <span className="metric-value">{analytics.total_routes}</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Active Buses:</span>
                  <span className="metric-value">{analytics.active_buses}</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Predictions:</span>
                  <span className="metric-value">{analytics.total_predictions}</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Avg Confidence:</span>
                  <span className="metric-value">{(analytics.average_confidence * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>
          )}
        </div>
        
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

const MapComponent = ({ selectedRoute, busLocations, predictions }) => {
  const [routeStops, setRouteStops] = useState([]);

  useEffect(() => {
    if (selectedRoute) {
      setRouteStops(selectedRoute.stops || []);
    } else {
      setRouteStops([]);
    }
  }, [selectedRoute]);

  // Default center (New York City)
  const defaultCenter = [40.7128, -74.0060];
  const defaultZoom = 12;

  // Create route polyline
  const routePolyline = routeStops.map(stop => [stop.latitude, stop.longitude]);

  // Group predictions by stop
  const predictionsByStop = predictions.reduce((acc, prediction) => {
    if (!acc[prediction.stop_id]) {
      acc[prediction.stop_id] = [];
    }
    acc[prediction.stop_id].push(prediction);
    return acc;
  }, {});

  return (
    <MapContainer
      center={defaultCenter}
      zoom={defaultZoom}
      style={{ height: '100%', width: '100%' }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* Route stops */}
      {routeStops.map((stop) => (
        <Marker
          key={stop.id}
          position={[stop.latitude, stop.longitude]}
          icon={createStopIcon()}
        >
          <Popup>
            <div>
              <h3>{stop.stop_name}</h3>
              <p>Stop ID: {stop.stop_id}</p>
              {predictionsByStop[stop.id] && (
                <div>
                  <h4>Upcoming Arrivals:</h4>
                  {predictionsByStop[stop.id].map((prediction) => (
                    <div key={prediction.id} style={{ margin: '5px 0' }}>
                      <strong>Bus {prediction.bus_id}</strong><br />
                      {new Date(prediction.predicted_arrival_time).toLocaleTimeString()}<br />
                      <small>Confidence: {(prediction.confidence_score * 100).toFixed(0)}%</small>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </Popup>
        </Marker>
      ))}

      {/* Route polyline */}
      {routePolyline.length > 1 && (
        <Polyline
          positions={routePolyline}
          color="#667eea"
          weight={4}
          opacity={0.7}
        />
      )}

      {/* Bus locations */}
      {busLocations.map((bus) => (
        <Marker
          key={bus.id}
          position={[bus.current_location?.latitude || 0, bus.current_location?.longitude || 0]}
          icon={createBusIcon()}
        >
          <Popup>
            <div>
              <h3>{bus.bus_number}</h3>
              <p>Route: {bus.route_id}</p>
              {bus.current_location && (
                <>
                  <p>Speed: {bus.current_location.speed?.toFixed(1)} km/h</p>
                  <p>Direction: {bus.current_location.direction?.toFixed(0)}°</p>
                  <p>Last Update: {new Date(bus.current_location.timestamp).toLocaleTimeString()}</p>
                </>
              )}
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
};

export default App;
