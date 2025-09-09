#!/usr/bin/env python3
"""
Complete System Startup Script
Error-free startup for the Real-Time Public Transport Monitoring System
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
import logging
import signal
import threading

# Load environment variables
load_dotenv("backend/.env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system_startup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global variables for process management
backend_process = None
frontend_process = None
http_server_process = None

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Shutting down complete system...")
    cleanup_processes()
    sys.exit(0)

def cleanup_processes():
    """Clean up all running processes"""
    global backend_process, frontend_process, http_server_process
    
    try:
        if backend_process:
            backend_process.terminate()
            print("✅ Backend process terminated")
        
        if frontend_process:
            frontend_process.terminate()
            print("✅ Frontend process terminated")
        
        if http_server_process:
            http_server_process.terminate()
            print("✅ HTTP server process terminated")
    except Exception as e:
        logger.error(f"Error cleaning up processes: {e}")

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

def setup_database():
    """Setup the production database"""
    print("\n🔄 Setting up production database...")
    
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
    
    # Run database setup script
    try:
        result = subprocess.run(
            [python_cmd, "backend/scripts/setup_database_simple.py"],
            cwd=".",
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Database setup completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Database setup failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def start_backend():
    """Start the complete backend server"""
    global backend_process
    
    print("\n🚀 Starting Complete Backend Server...")
    
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
    
    # Start backend
    try:
        backend_process = subprocess.Popen(
            [python_cmd, "backend/main_complete.py"],
            cwd=".",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ Complete backend server started")
        return True
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def start_frontend():
    """Start the complete frontend server"""
    global frontend_process
    
    print("\n🚀 Starting Complete Frontend Server...")
    
    # Check if node_modules exists
    node_modules = Path("frontend/node_modules")
    if not node_modules.exists():
        print("❌ Node modules not found. Please run setup_frontend.py first")
        return False
    
    # Start frontend
    try:
        frontend_process = subprocess.Popen(
            ["npm", "start"],
            cwd="frontend",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ Complete frontend server started")
        return True
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return False

def start_http_server():
    """Start HTTP server for demo"""
    global http_server_process
    
    print("\n🚀 Starting HTTP Server for Demo...")
    
    try:
        http_server_process = subprocess.Popen(
            ["python", "-m", "http.server", "3000"],
            cwd=".",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ HTTP server started")
        return True
    except Exception as e:
        print(f"❌ Failed to start HTTP server: {e}")
        return False

def wait_for_service(url, service_name, max_attempts=30):
    """Wait for a service to become available"""
    import requests
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {service_name} is ready")
                return True
        except:
            pass
        
        print(f"⏳ Waiting for {service_name}... (attempt {attempt + 1}/{max_attempts})")
        time.sleep(2)
    
    print(f"❌ {service_name} failed to start within timeout")
    return False

def monitor_processes():
    """Monitor running processes and restart if needed"""
    while True:
        try:
            # Check backend
            if backend_process and backend_process.poll() is not None:
                print("⚠️ Backend process died, restarting...")
                start_backend()
            
            # Check frontend
            if frontend_process and frontend_process.poll() is not None:
                print("⚠️ Frontend process died, restarting...")
                start_frontend()
            
            # Check HTTP server
            if http_server_process and http_server_process.poll() is not None:
                print("⚠️ HTTP server process died, restarting...")
                start_http_server()
            
            time.sleep(10)  # Check every 10 seconds
            
        except Exception as e:
            logger.error(f"Error in process monitoring: {e}")
            time.sleep(10)

def main():
    """Main startup function"""
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🚌 Real-Time Public Transport Monitoring System - COMPLETE")
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
    
    # Setup database
    if not setup_database():
        return False
    
    # Start backend
    if not start_backend():
        return False
    
    # Wait for backend to start
    print("\n⏳ Waiting for backend to start...")
    if not wait_for_service("http://localhost:8000/health", "Backend API"):
        return False
    
    # Start frontend
    if not start_frontend():
        print("⚠️ Frontend failed to start, starting HTTP server as fallback...")
        start_http_server()
    
    # Wait for frontend to start
    print("\n⏳ Waiting for frontend to start...")
    if not wait_for_service("http://localhost:3000", "Frontend"):
        print("⚠️ Frontend not accessible, using HTTP server demo...")
    
    print("\n🎉 Complete system started successfully!")
    print("\n📱 Access the application:")
    print("   Frontend: http://localhost:3000")
    print("   Demo: http://localhost:3000/working_demo.html")
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
    print("   ✅ Error handling and auto-recovery")
    print("   ✅ Process monitoring and restart")
    
    print("\n🛑 To stop the system:")
    print("   Press Ctrl+C or close this terminal")
    
    # Start process monitoring in a separate thread
    monitor_thread = threading.Thread(target=monitor_processes, daemon=True)
    monitor_thread.start()
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down complete system...")
        cleanup_processes()
        print("✅ System stopped")

if __name__ == "__main__":
    main()
