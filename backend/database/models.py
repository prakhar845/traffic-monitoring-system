from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Route(Base):
    __tablename__ = "routes"
    
    id = Column(Integer, primary_key=True, index=True)
    route_number = Column(String(10), unique=True, index=True)
    route_name = Column(String(100))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    stops = relationship("RouteStop", back_populates="route")
    buses = relationship("Bus", back_populates="route")
    predictions = relationship("Prediction", back_populates="route")

class BusStop(Base):
    __tablename__ = "bus_stops"
    
    id = Column(Integer, primary_key=True, index=True)
    stop_id = Column(String(20), unique=True, index=True)
    stop_name = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    address = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    route_stops = relationship("RouteStop", back_populates="stop")
    predictions = relationship("Prediction", back_populates="stop")

class RouteStop(Base):
    __tablename__ = "route_stops"
    
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"))
    stop_id = Column(Integer, ForeignKey("bus_stops.id"))
    sequence_order = Column(Integer)
    estimated_travel_time = Column(Integer)  # seconds to next stop
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    route = relationship("Route", back_populates="stops")
    stop = relationship("BusStop", back_populates="route_stops")

class Bus(Base):
    __tablename__ = "buses"
    
    id = Column(Integer, primary_key=True, index=True)
    bus_number = Column(String(20), unique=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"))
    capacity = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    route = relationship("Route", back_populates="buses")
    locations = relationship("BusLocation", back_populates="bus")

class BusLocation(Base):
    __tablename__ = "bus_locations"
    
    id = Column(Integer, primary_key=True, index=True)
    bus_id = Column(Integer, ForeignKey("buses.id"))
    latitude = Column(Float)
    longitude = Column(Float)
    speed = Column(Float)  # km/h
    direction = Column(Float)  # degrees
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    bus = relationship("Bus", back_populates="locations")

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"))
    stop_id = Column(Integer, ForeignKey("bus_stops.id"))
    bus_id = Column(Integer, ForeignKey("buses.id"))
    predicted_arrival_time = Column(DateTime)
    confidence_score = Column(Float)  # 0-1
    prediction_type = Column(String(20))  # 'lstm', 'prophet', 'historical'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    route = relationship("Route", back_populates="predictions")
    stop = relationship("BusStop", back_populates="predictions")
    bus = relationship("Bus")

class TrafficCondition(Base):
    __tablename__ = "traffic_conditions"
    
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"))
    segment_start_lat = Column(Float)
    segment_start_lng = Column(Float)
    segment_end_lat = Column(Float)
    segment_end_lng = Column(Float)
    traffic_level = Column(String(20))  # 'light', 'moderate', 'heavy', 'severe'
    average_speed = Column(Float)  # km/h
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    route = relationship("Route")
