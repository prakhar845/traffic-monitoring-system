import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Routes API
export const routesAPI = {
  getAll: () => api.get('/routes/'),
  getById: (id) => api.get(`/routes/${id}`),
  getBuses: (id) => api.get(`/routes/${id}/buses`),
};

// Buses API
export const busesAPI = {
  getAll: () => api.get('/buses/'),
  getById: (id) => api.get(`/buses/${id}`),
  getLocation: (id) => api.get(`/buses/${id}/location`),
  getHistory: (id, limit = 100) => api.get(`/buses/${id}/history?limit=${limit}`),
  updateLocation: (id, latitude, longitude, speed = 0, direction = 0) =>
    api.post(`/buses/${id}/location`, {
      latitude,
      longitude,
      speed,
      direction,
    }),
};

// Stops API
export const stopsAPI = {
  getAll: () => api.get('/stops/'),
  getById: (id) => api.get(`/stops/${id}`),
  getNearby: (latitude, longitude, radius = 1.0) =>
    api.get(`/stops/nearby/${latitude}/${longitude}?radius=${radius}`),
};

// Predictions API
export const predictionsAPI = {
  getAll: (routeId = null, stopId = null, busId = null) => {
    const params = new URLSearchParams();
    if (routeId) params.append('route_id', routeId);
    if (stopId) params.append('stop_id', stopId);
    if (busId) params.append('bus_id', busId);
    
    return api.get(`/predictions/?${params.toString()}`);
  },
  getForStop: (stopId) => api.get(`/predictions/stop/${stopId}`),
  getForRoute: (routeId) => api.get(`/predictions/route/${routeId}`),
  generateForBus: (busId) => api.post(`/predictions/generate/${busId}`),
};

// Health check
export const healthAPI = {
  check: () => api.get('/health'),
};

export default api;
