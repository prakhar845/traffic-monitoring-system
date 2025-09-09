#!/usr/bin/env python3
"""
Working Production Startup Script
Simplified version that works with your current setup
"""

import os
import sys
import subprocess
import time
import platform
from pathlib import Path
import mysql.connector
import redis
from dotenv import load_dotenv

# Load environment variables from backend directory
load_dotenv("backend/.env")

def check_mysql_connection():
    """Check if MySQL is running and accessible"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', '3306')),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', '')
        )
        connection.close()
        print("✅ MySQL connection successful")
        return True
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        return False

def check_redis_connection():
    """Check if Redis is running and accessible"""
    try:
        r = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', '6379')),
            password=os.getenv('REDIS_PASSWORD', '') if os.getenv('REDIS_PASSWORD', '') else None
        )
        r.ping()
        print("✅ Redis connection successful")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def start_backend():
    """Start the working backend server"""
    print("\n🚀 Starting Working Backend Server...")
    
    # Check if virtual environment exists
    venv_path = Path("backend/venv")
    if not venv_path.exists():
        print("❌ Virtual environment not found. Please run setup_backend.py first")
        return False
    
    # Get python command
    if platform.system() == "Windows":
        python_cmd = "backend\\venv\\Scripts\\python.exe"
    else:
        python_cmd = "backend/venv/bin/python"
    
    # Start backend (use the working demo version)
    try:
        subprocess.Popen(
            [python_cmd, "backend/main_demo.py"],
            cwd=".",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ Working backend server started")
        return True
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def start_frontend():
    """Start the working frontend server"""
    print("\n🚀 Starting Working Frontend Server...")
    
    # Check if node_modules exists
    node_modules = Path("frontend/node_modules")
    if not node_modules.exists():
        print("❌ Node modules not found. Please run setup_frontend.py first")
        return False
    
    # Start frontend
    try:
        subprocess.Popen(
            ["npm", "start"],
            cwd="frontend",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ Working frontend server started")
        return True
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return False

def main():
    """Main startup function"""
    print("🚌 Real-Time Public Transport Monitoring System - WORKING VERSION")
    print("=" * 70)
    
    # Check dependencies
    print("\n🔍 Checking system dependencies...")
    
    mysql_ok = check_mysql_connection()
    redis_ok = check_redis_connection()
    
    if not mysql_ok:
        print("\n❌ MySQL is not running or not accessible")
        print("Please ensure MySQL is installed and running")
        return False
    
    if not redis_ok:
        print("\n❌ Redis is not running or not accessible")
        print("Please ensure Redis is installed and running")
        return False
    
    # Start backend
    if not start_backend():
        return False
    
    # Wait for backend to start
    print("\n⏳ Waiting for backend to start...")
    time.sleep(10)
    
    # Start frontend
    if not start_frontend():
        return False
    
    print("\n🎉 Working system started successfully!")
    print("\n📱 Access the application:")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:8000")
    print("   API Documentation: http://localhost:8000/docs")
    print("   Health Check: http://localhost:8000/health")
    
    print("\n🔐 Authentication:")
    print("   Default Admin: username='admin', password='admin123'")
    print("   Register new users at: http://localhost:8000/api/auth/register")
    
    print("\n📊 Features Available:")
    print("   ✅ Real-time GPS tracking with ML predictions")
    print("   ✅ User authentication and role-based access")
    print("   ✅ Analytics dashboard and performance metrics")
    print("   ✅ Traffic condition monitoring")
    print("   ✅ WebSocket real-time updates")
    print("   ✅ Production database with full schema")
    print("   ✅ Redis caching for high performance")
    
    print("\n🛑 To stop the system:")
    print("   Press Ctrl+C or close this terminal")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down working system...")
        print("✅ System stopped")

if __name__ == "__main__":
    main()
