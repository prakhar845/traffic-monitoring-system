#!/usr/bin/env python3
"""
Find MySQL Configuration Script
Tries different ways to connect to MySQL
"""

import mysql.connector
from mysql.connector import Error
import subprocess
import os
import sys

def try_mysql_connection():
    """Try different MySQL connection methods"""
    
    # Common MySQL configurations
    configs = [
        # No password
        {'host': 'localhost', 'port': 3306, 'user': 'root', 'password': ''},
        # Common passwords
        {'host': 'localhost', 'port': 3306, 'user': 'root', 'password': 'root'},
        {'host': 'localhost', 'port': 3306, 'user': 'root', 'password': 'password'},
        {'host': 'localhost', 'port': 3306, 'user': 'root', 'password': 'admin'},
        {'host': 'localhost', 'port': 3306, 'user': 'root', 'password': '123456'},
        {'host': 'localhost', 'port': 3306, 'user': 'root', 'password': 'mysql'},
        # Different ports
        {'host': 'localhost', 'port': 3307, 'user': 'root', 'password': ''},
        {'host': 'localhost', 'port': 3307, 'user': 'root', 'password': 'root'},
        # Different users
        {'host': 'localhost', 'port': 3306, 'user': 'mysql', 'password': ''},
        {'host': 'localhost', 'port': 3306, 'user': 'mysql', 'password': 'mysql'},
    ]
    
    print("🔍 Trying different MySQL configurations...")
    
    for i, config in enumerate(configs):
        try:
            print(f"Trying {i+1}: {config['user']}@{config['host']}:{config['port']} (password: {'***' if config['password'] else 'none'})")
            connection = mysql.connector.connect(**config)
            print(f"✅ SUCCESS! Configuration {i+1} works!")
            print(f"   Host: {config['host']}")
            print(f"   Port: {config['port']}")
            print(f"   User: {config['user']}")
            print(f"   Password: {'***' if config['password'] else 'none'}")
            
            # Test database creation
            cursor = connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS traffic_monitoring")
            print("✅ Database 'traffic_monitoring' created successfully!")
            
            connection.close()
            return config
            
        except Error as e:
            print(f"❌ Configuration {i+1} failed: {e}")
            continue
    
    return None

def check_mysql_service():
    """Check if MySQL service is running"""
    print("\n🔍 Checking MySQL service status...")
    
    try:
        # Try to find MySQL service
        result = subprocess.run(['sc', 'query', 'mysql'], capture_output=True, text=True, shell=True)
        if 'RUNNING' in result.stdout:
            print("✅ MySQL service is running")
        else:
            print("❌ MySQL service is not running")
            print("Try starting it with: net start mysql")
    except Exception as e:
        print(f"⚠️ Could not check MySQL service: {e}")

def check_mysql_processes():
    """Check for MySQL processes"""
    print("\n🔍 Checking for MySQL processes...")
    
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq mysqld.exe'], capture_output=True, text=True, shell=True)
        if 'mysqld.exe' in result.stdout:
            print("✅ MySQL process (mysqld.exe) is running")
        else:
            print("❌ MySQL process (mysqld.exe) not found")
    except Exception as e:
        print(f"⚠️ Could not check MySQL processes: {e}")

def check_mysql_ports():
    """Check what's running on MySQL ports"""
    print("\n🔍 Checking MySQL ports...")
    
    ports = [3306, 3307, 3308]
    for port in ports:
        try:
            result = subprocess.run(['netstat', '-an'], capture_output=True, text=True, shell=True)
            if f':{port}' in result.stdout:
                print(f"✅ Port {port} is in use")
            else:
                print(f"❌ Port {port} is not in use")
        except Exception as e:
            print(f"⚠️ Could not check port {port}: {e}")

def main():
    """Main function"""
    print("🚌 MySQL Configuration Finder")
    print("=" * 40)
    
    # Check MySQL service
    check_mysql_service()
    
    # Check MySQL processes
    check_mysql_processes()
    
    # Check MySQL ports
    check_mysql_ports()
    
    # Try connections
    config = try_mysql_connection()
    
    if config:
        print(f"\n🎉 Found working MySQL configuration!")
        print(f"Use this in your .env file:")
        print(f"MYSQL_HOST={config['host']}")
        print(f"MYSQL_PORT={config['port']}")
        print(f"MYSQL_USER={config['user']}")
        print(f"MYSQL_PASSWORD={config['password']}")
        print(f"MYSQL_DATABASE=traffic_monitoring")
        
        # Update .env file
        update_env_file(config)
        
    else:
        print("\n❌ Could not find working MySQL configuration")
        print("\n🔧 Troubleshooting steps:")
        print("1. Make sure MySQL is installed and running")
        print("2. Check if MySQL service is started: net start mysql")
        print("3. Try connecting with MySQL Workbench or command line")
        print("4. Check if MySQL is running on a different port")
        print("5. Verify MySQL root password")

def update_env_file(config):
    """Update .env file with working configuration"""
    try:
        env_file = "backend/.env"
        
        # Create .env file content
        env_content = f"""# MySQL Configuration
MYSQL_HOST={config['host']}
MYSQL_PORT={config['port']}
MYSQL_USER={config['user']}
MYSQL_PASSWORD={config['password']}
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
        
        print(f"\n✅ Updated {env_file} with working configuration")
        
    except Exception as e:
        print(f"⚠️ Warning: Could not update .env file: {e}")

if __name__ == "__main__":
    main()
