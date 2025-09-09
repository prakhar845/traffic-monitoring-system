#!/usr/bin/env python3
"""
MySQL Configuration Script
Helps you set up MySQL with your known password
"""

import mysql.connector
from mysql.connector import Error
import os
import getpass

def test_mysql_connection(host, port, user, password):
    """Test MySQL connection with provided credentials"""
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password
        )
        print("✅ MySQL connection successful!")
        connection.close()
        return True
    except Error as e:
        print(f"❌ MySQL connection failed: {e}")
        return False

def create_database_and_tables(host, port, user, password):
    """Create database and tables"""
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password
        )
        cursor = connection.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS traffic_monitoring")
        print("✅ Database 'traffic_monitoring' created successfully")
        
        # Use the database
        cursor.execute("USE traffic_monitoring")
        
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
            print(f"✅ Table created successfully")
        
        # Insert sample data
        insert_sample_data(cursor)
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("✅ Database setup completed successfully!")
        return True
        
    except Error as e:
        print(f"❌ Error setting up database: {e}")
        return False

def insert_sample_data(cursor):
    """Insert sample data into the database"""
    try:
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
        print(f"✅ Inserted {len(routes_data)} routes")
        
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
        print(f"✅ Inserted {len(stops_data)} bus stops")
        
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
        print(f"✅ Inserted {len(route_stops_data)} route-stop relationships")
        
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
        print(f"✅ Inserted {len(buses_data)} buses")
        
        # Insert sample user
        cursor.execute(
            "INSERT IGNORE INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)",
            ('admin', 'admin@trafficmonitoring.com', 'hashed_password_here', 'admin')
        )
        print("✅ Inserted admin user")
        
        print("✅ Sample data inserted successfully")
        
    except Error as e:
        print(f"❌ Error inserting sample data: {e}")

def update_env_file(host, port, user, password):
    """Update .env file with working configuration"""
    try:
        env_file = "backend/.env"
        
        # Create .env file content
        env_content = f"""# MySQL Configuration
MYSQL_HOST={host}
MYSQL_PORT={port}
MYSQL_USER={user}
MYSQL_PASSWORD={password}
MYSQL_DATABASE=traffic_monitoring

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# Security Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"✅ Updated {env_file} with working configuration")
        
    except Exception as e:
        print(f"⚠️ Warning: Could not update .env file: {e}")

def main():
    """Main function"""
    print("🚌 MySQL Configuration for Traffic Monitoring System")
    print("=" * 60)
    
    # Get MySQL credentials
    print("\n📝 Please enter your MySQL credentials:")
    host = input("MySQL Host (default: localhost): ").strip() or "localhost"
    port = input("MySQL Port (default: 3306): ").strip() or "3306"
    user = input("MySQL Username (default: root): ").strip() or "root"
    password = getpass.getpass("MySQL Password: ")
    
    # Convert port to int
    try:
        port = int(port)
    except ValueError:
        print("❌ Invalid port number. Using default 3306")
        port = 3306
    
    print(f"\n🔍 Testing connection to {user}@{host}:{port}...")
    
    # Test connection
    if test_mysql_connection(host, port, user, password):
        print("\n🔄 Setting up database and tables...")
        
        # Create database and tables
        if create_database_and_tables(host, port, user, password):
            print("\n📝 Updating configuration file...")
            
            # Update .env file
            update_env_file(host, port, user, password)
            
            print("\n🎉 MySQL setup completed successfully!")
            print("\n📊 Database contains:")
            print("   - 5 routes with full stop sequences")
            print("   - 10 bus stops with GPS coordinates")
            print("   - 7 buses across different routes")
            print("   - User management system")
            print("   - Traffic monitoring tables")
            print("   - Prediction and logging systems")
            
            print("\n🚀 You can now run the production system:")
            print("   python start_production.py")
            
            return True
        else:
            print("\n❌ Database setup failed")
            return False
    else:
        print("\n❌ Could not connect to MySQL")
        print("Please check your credentials and try again")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Setup completed successfully!")
    else:
        print("\n❌ Setup failed. Please check your MySQL configuration.")
