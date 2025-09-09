from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "traffic_monitoring")

# Create database URL
DATABASE_URL = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

# Create engine
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    pool_pre_ping=True,
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    from .models import Base
    Base.metadata.create_all(bind=engine)

def init_database():
    """Initialize database with sample data"""
    from .models import Base, Route, BusStop, RouteStop, Bus
    from sqlalchemy.orm import Session
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(Route).first():
            return
        
        # Create sample routes
        routes_data = [
            {"route_number": "101", "route_name": "Downtown Express", "description": "Express route from downtown to airport"},
            {"route_number": "202", "route_name": "University Line", "description": "Route connecting university to city center"},
            {"route_number": "303", "route_name": "Suburban Loop", "description": "Circular route through suburban areas"},
        ]
        
        routes = []
        for route_data in routes_data:
            route = Route(**route_data)
            db.add(route)
            routes.append(route)
        
        db.commit()
        
        # Create sample bus stops
        stops_data = [
            {"stop_id": "ST001", "stop_name": "Downtown Central", "latitude": 40.7128, "longitude": -74.0060},
            {"stop_id": "ST002", "stop_name": "University Gate", "latitude": 40.7589, "longitude": -73.9851},
            {"stop_id": "ST003", "stop_name": "Airport Terminal", "latitude": 40.6413, "longitude": -73.7781},
            {"stop_id": "ST004", "stop_name": "City Hall", "latitude": 40.7128, "longitude": -74.0060},
            {"stop_id": "ST005", "stop_name": "Shopping Mall", "latitude": 40.7505, "longitude": -73.9934},
        ]
        
        stops = []
        for stop_data in stops_data:
            stop = BusStop(**stop_data)
            db.add(stop)
            stops.append(stop)
        
        db.commit()
        
        # Create route-stop relationships
        route_stops_data = [
            # Route 101: Downtown to Airport
            {"route_id": routes[0].id, "stop_id": stops[0].id, "sequence_order": 1, "estimated_travel_time": 300},
            {"route_id": routes[0].id, "stop_id": stops[3].id, "sequence_order": 2, "estimated_travel_time": 600},
            {"route_id": routes[0].id, "stop_id": stops[2].id, "sequence_order": 3, "estimated_travel_time": 0},
            
            # Route 202: University Line
            {"route_id": routes[1].id, "stop_id": stops[1].id, "sequence_order": 1, "estimated_travel_time": 240},
            {"route_id": routes[1].id, "stop_id": stops[0].id, "sequence_order": 2, "estimated_travel_time": 480},
            {"route_id": routes[1].id, "stop_id": stops[4].id, "sequence_order": 3, "estimated_travel_time": 360},
            
            # Route 303: Suburban Loop
            {"route_id": routes[2].id, "stop_id": stops[4].id, "sequence_order": 1, "estimated_travel_time": 180},
            {"route_id": routes[2].id, "stop_id": stops[1].id, "sequence_order": 2, "estimated_travel_time": 420},
            {"route_id": routes[2].id, "stop_id": stops[3].id, "sequence_order": 3, "estimated_travel_time": 300},
        ]
        
        for route_stop_data in route_stops_data:
            route_stop = RouteStop(**route_stop_data)
            db.add(route_stop)
        
        db.commit()
        
        # Create sample buses
        buses_data = [
            {"bus_number": "BUS001", "route_id": routes[0].id, "capacity": 50},
            {"bus_number": "BUS002", "route_id": routes[0].id, "capacity": 50},
            {"bus_number": "BUS003", "route_id": routes[1].id, "capacity": 40},
            {"bus_number": "BUS004", "route_id": routes[1].id, "capacity": 40},
            {"bus_number": "BUS005", "route_id": routes[2].id, "capacity": 35},
        ]
        
        for bus_data in buses_data:
            bus = Bus(**bus_data)
            db.add(bus)
        
        db.commit()
        
        print("Database initialized with sample data")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()
