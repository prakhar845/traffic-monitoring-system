import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, CircleMarker } from 'react-leaflet';
import L from 'leaflet';
import { Bus, MapPin, Clock } from 'lucide-react';

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

const MapComponent = ({ selectedRoute, busLocations, predictions }) => {
  const mapRef = useRef();

  // Default center (New York City)
  const defaultCenter = [40.7128, -74.0060];
  const defaultZoom = 12;

  // Get route stops if a route is selected
  const [routeStops, setRouteStops] = React.useState([]);

  useEffect(() => {
    if (selectedRoute) {
      loadRouteStops(selectedRoute.id);
    } else {
      setRouteStops([]);
    }
  }, [selectedRoute]);

  const loadRouteStops = async (routeId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/routes/${routeId}`);
      const routeData = await response.json();
      setRouteStops(routeData.stops || []);
    } catch (error) {
      console.error('Error loading route stops:', error);
    }
  };

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
      ref={mapRef}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* Route stops */}
      {routeStops.map((stop) => (
        <Marker
          key={stop.stop_id}
          position={[stop.latitude, stop.longitude]}
          icon={createStopIcon()}
        >
          <Popup>
            <div>
              <h3>{stop.stop_name}</h3>
              <p>Stop ID: {stop.stop_id}</p>
              <p>Sequence: {stop.sequence_order}</p>
              {predictionsByStop[stop.stop_id] && (
                <div>
                  <h4>Upcoming Arrivals:</h4>
                  {predictionsByStop[stop.stop_id].map((prediction) => (
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
      {busLocations.map((location) => (
        <Marker
          key={location.bus_id}
          position={[location.latitude, location.longitude]}
          icon={createBusIcon()}
        >
          <Popup>
            <div>
              <h3>Bus {location.bus_id}</h3>
              <p>Speed: {location.speed?.toFixed(1)} km/h</p>
              <p>Direction: {location.direction?.toFixed(0)}°</p>
              <p>Last Update: {new Date(location.timestamp).toLocaleTimeString()}</p>
            </div>
          </Popup>
        </Marker>
      ))}

      {/* Speed indicators for buses */}
      {busLocations.map((location) => {
        if (location.speed > 0) {
          const radius = Math.min(Math.max(location.speed * 2, 50), 200);
          return (
            <CircleMarker
              key={`speed-${location.bus_id}`}
              center={[location.latitude, location.longitude]}
              radius={radius / 10}
              color="#ff6b6b"
              fillColor="#ff6b6b"
              fillOpacity={0.2}
              weight={1}
            />
          );
        }
        return null;
      })}
    </MapContainer>
  );
};

export default MapComponent;
