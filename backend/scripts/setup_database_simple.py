#!/usr/bin/env python3
"""
Simple Database Setup Script
Creates the traffic_monitoring database with sample data
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import sys

load_dotenv("backend/.env")

def create_database():
    """Create the traffic_monitoring database"""
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', '3306')),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', '')
        )
        
        cursor = connection.cursor()
        
        # Create database
        database_name = os.getenv('MYSQL_DATABASE', 'traffic_monitoring')
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        print(f"Database '{database_name}' created successfully")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
        print(f"Error creating database: {e}")
        return False

def create_tables():
    """Create all database tables"""
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', '3306')),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DATABASE', 'traffic_monitoring')
        )
        
        cursor = connection.cursor()
        
        # Create tables
        tables = [
            """
            CREATE TABLE IF NOT EXISTS routes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                route_number VARCHAR(10) UNIQUE NOT NULL,
                route_name VARCHAR(100) NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS bus_stops (
                id INT AUTO_INCREMENT PRIMARY KEY,
                stop_id VARCHAR(20) UNIQUE NOT NULL,
                stop_name VARCHAR(100) NOT NULL,
                latitude DECIMAL(10, 8) NOT NULL,
                longitude DECIMAL(11, 8) NOT NULL,
                address TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS route_stops (
                id INT AUTO_INCREMENT PRIMARY KEY,
                route_id INT NOT NULL,
                stop_id INT NOT NULL,
                sequence_order INT NOT NULL,
                estimated_travel_time INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE,
                FOREIGN KEY (stop_id) REFERENCES bus_stops(id) ON DELETE CASCADE,
                UNIQUE KEY unique_route_stop (route_id, stop_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS buses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                bus_number VARCHAR(20) UNIQUE NOT NULL,
                route_id INT NOT NULL,
                capacity INT DEFAULT 50,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS bus_locations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                bus_id INT NOT NULL,
                latitude DECIMAL(10, 8) NOT NULL,
                longitude DECIMAL(11, 8) NOT NULL,
                speed DECIMAL(5, 2) DEFAULT 0.00,
                direction DECIMAL(5, 2) DEFAULT 0.00,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (bus_id) REFERENCES buses(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                route_id INT NOT NULL,
                stop_id INT NOT NULL,
                bus_id INT NOT NULL,
                predicted_arrival_time TIMESTAMP NOT NULL,
                confidence_score DECIMAL(3, 2) DEFAULT 0.00,
                prediction_type VARCHAR(20) DEFAULT 'simple',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE,
                FOREIGN KEY (stop_id) REFERENCES bus_stops(id) ON DELETE CASCADE,
                FOREIGN KEY (bus_id) REFERENCES buses(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS traffic_conditions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                route_id INT NOT NULL,
                segment_start_lat DECIMAL(10, 8) NOT NULL,
                segment_start_lng DECIMAL(11, 8) NOT NULL,
                segment_end_lat DECIMAL(10, 8) NOT NULL,
                segment_end_lng DECIMAL(11, 8) NOT NULL,
                traffic_level ENUM('light', 'moderate', 'heavy', 'severe') DEFAULT 'moderate',
                average_speed DECIMAL(5, 2) DEFAULT 0.00,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role ENUM('admin', 'operator', 'viewer') DEFAULT 'viewer',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS system_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                level ENUM('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL') NOT NULL,
                message TEXT NOT NULL,
                module VARCHAR(50),
                user_id INT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
            """
        ]
        
        for table_sql in tables:
            cursor.execute(table_sql)
            print("Table created successfully")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("All tables created successfully")
        return True
        
    except Error as e:
        print(f"Error creating tables: {e}")
        return False

def insert_sample_data():
    """Insert sample data into the database"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', '3306')),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DATABASE', 'traffic_monitoring')
        )
        
        cursor = connection.cursor()
        
        # Insert routes
        routes_data = [
            ('101', 'Downtown Express', 'Express route from downtown to airport via city center'),
            ('202', 'University Line', 'Route connecting university to city center and shopping districts'),
            ('303', 'Suburban Loop', 'Circular route through suburban residential areas'),
            ('404', 'Industrial Zone', 'Route serving industrial areas and warehouses'),
            ('505', 'Beach Express', 'Scenic route along the coastline to beach areas')
        ]
        
        cursor.executemany(
            "INSERT IGNORE INTO routes (route_number, route_name, description) VALUES (%s, %s, %s)",
            routes_data
        )
        print(f"Inserted {len(routes_data)} routes")
        
        # Insert bus stops
        stops_data = [
            ('ST001', 'Downtown Central', 40.7128, -74.0060, 'Main downtown transportation hub'),
            ('ST002', 'University Gate', 40.7589, -73.9851, 'Main entrance to university campus'),
            ('ST003', 'Airport Terminal', 40.6413, -73.7781, 'International airport terminal'),
            ('ST004', 'City Hall', 40.7130, -74.0055, 'Government building and civic center'),
            ('ST005', 'Shopping Mall', 40.7505, -73.9934, 'Large shopping and entertainment complex'),
            ('ST006', 'Industrial Park', 40.6892, -74.0445, 'Industrial and manufacturing area'),
            ('ST007', 'Beach Front', 40.5689, -73.9857, 'Popular beach and recreation area'),
            ('ST008', 'Suburban Center', 40.7831, -73.9712, 'Suburban commercial district'),
            ('ST009', 'Tech Campus', 40.7282, -74.0776, 'Technology and business campus'),
            ('ST010', 'Hospital District', 40.7614, -73.9776, 'Medical center and hospital area')
        ]
        
        cursor.executemany(
            "INSERT IGNORE INTO bus_stops (stop_id, stop_name, latitude, longitude, address) VALUES (%s, %s, %s, %s, %s)",
            stops_data
        )
        print(f"Inserted {len(stops_data)} bus stops")
        
        # Insert route-stop relationships
        route_stops_data = [
            # Route 101: Downtown Express
            (1, 1, 1, 300),  # Downtown Central -> City Hall (5 min)
            (1, 4, 2, 600),  # City Hall -> Airport Terminal (10 min)
            (1, 3, 3, 0),    # Airport Terminal (end)
            
            # Route 202: University Line
            (2, 2, 1, 240),  # University Gate -> Downtown Central (4 min)
            (2, 1, 2, 480),  # Downtown Central -> Shopping Mall (8 min)
            (2, 5, 3, 0),    # Shopping Mall (end)
            
            # Route 303: Suburban Loop
            (3, 8, 1, 180),  # Suburban Center -> University Gate (3 min)
            (3, 2, 2, 420),  # University Gate -> Hospital District (7 min)
            (3, 10, 3, 0),   # Hospital District (end)
            
            # Route 404: Industrial Zone
            (4, 6, 1, 360),  # Industrial Park -> Tech Campus (6 min)
            (4, 9, 2, 0),    # Tech Campus (end)
            
            # Route 505: Beach Express
            (5, 7, 1, 0),    # Beach Front (end)
        ]
        
        cursor.executemany(
            "INSERT IGNORE INTO route_stops (route_id, stop_id, sequence_order, estimated_travel_time) VALUES (%s, %s, %s, %s)",
            route_stops_data
        )
        print(f"Inserted {len(route_stops_data)} route-stop relationships")
        
        # Insert buses
        buses_data = [
            ('BUS001', 1, 50),  # Route 101
            ('BUS002', 1, 50),  # Route 101
            ('BUS003', 2, 40),  # Route 202
            ('BUS004', 2, 40),  # Route 202
            ('BUS005', 3, 35),  # Route 303
            ('BUS006', 4, 45),  # Route 404
            ('BUS007', 5, 30),  # Route 505
        ]
        
        cursor.executemany(
            "INSERT IGNORE INTO buses (bus_number, route_id, capacity) VALUES (%s, %s, %s)",
            buses_data
        )
        print(f"Inserted {len(buses_data)} buses")
        
        # Insert sample user
        cursor.execute(
            "INSERT IGNORE INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)",
            ('admin', 'admin@trafficmonitoring.com', 'hashed_password_here', 'admin')
        )
        print("Inserted admin user")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("Sample data inserted successfully")
        return True
        
    except Error as e:
        print(f"Error inserting sample data: {e}")
        return False

def main():
    """Main setup function"""
    print("Setting up Production Database for Traffic Monitoring System")
    print("=" * 60)
    
    # Check if MySQL is running
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', '3306')),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', '')
        )
        connection.close()
        print("MySQL connection successful")
    except Error as e:
        print(f"Cannot connect to MySQL: {e}")
        print("Please ensure MySQL is running and credentials are correct in .env file")
        return False
    
    # Create database
    if not create_database():
        return False
    
    # Create tables
    if not create_tables():
        return False
    
    # Insert sample data
    if not insert_sample_data():
        return False
    
    print("\nDatabase setup completed successfully!")
    print("\nDatabase contains:")
    print("   - 5 routes with full stop sequences")
    print("   - 10 bus stops with GPS coordinates")
    print("   - 7 buses across different routes")
    print("   - User management system")
    print("   - Traffic monitoring tables")
    print("   - Prediction and logging systems")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
