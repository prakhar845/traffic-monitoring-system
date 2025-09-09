#!/usr/bin/env python3
"""
Startup script for the Real-Time Public Transport Monitoring System
"""

import os
import sys
import subprocess
import time
import platform
from pathlib import Path

def run_command(command, description, cwd=None, background=False):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        if background:
            # Run in background
            if platform.system() == "Windows":
                subprocess.Popen(command, shell=True, cwd=cwd)
            else:
                subprocess.Popen(command, shell=True, cwd=cwd, preexec_fn=os.setsid)
            print(f"✅ {description} started in background")
            return True
        else:
            result = subprocess.run(command, shell=True, check=True, cwd=cwd)
            print(f"✅ {description} completed successfully")
            return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e}")
        return False

def check_dependencies():
    """Check if required services are running"""
    print("🔍 Checking dependencies...")
    
    # Check MySQL
    try:
        import mysql.connector
        print("✅ MySQL connector available")
    except ImportError:
        print("❌ MySQL connector not found. Run: pip install mysql-connector-python")
        return False
    
    # Check Redis
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis is running")
    except:
        print("❌ Redis is not running. Please start Redis server")
        return False
    
    return True

def start_backend():
    """Start the backend server"""
    print("\n🚀 Starting Backend Server...")
    
    # Check if virtual environment exists
    venv_path = Path("backend/venv")
    if not venv_path.exists():
        print("❌ Virtual environment not found. Please run setup_backend.py first")
        return False
    
    # Get activation command
    if platform.system() == "Windows":
        python_cmd = "backend\\venv\\Scripts\\python"
    else:
        python_cmd = "backend/venv/bin/python"
    
    # Start backend
    return run_command(
        f"{python_cmd} main.py",
        "Starting FastAPI backend server",
        cwd="backend",
        background=True
    )

def start_frontend():
    """Start the frontend development server"""
    print("\n🚀 Starting Frontend Server...")
    
    # Check if node_modules exists
    node_modules = Path("frontend/node_modules")
    if not node_modules.exists():
        print("❌ Node modules not found. Please run setup_frontend.py first")
        return False
    
    # Start frontend
    return run_command(
        "npm start",
        "Starting React frontend server",
        cwd="frontend",
        background=True
    )

def start_gps_simulator():
    """Start GPS data simulator"""
    print("\n🚀 Starting GPS Data Simulator...")
    
    # Wait a bit for backend to start
    time.sleep(5)
    
    # Get activation command
    if platform.system() == "Windows":
        python_cmd = "backend\\venv\\Scripts\\python"
    else:
        python_cmd = "backend/venv/bin/python"
    
    # Start GPS simulator
    return run_command(
        f"{python_cmd} scripts/simulate_gps_data.py",
        "Starting GPS data simulator",
        cwd="backend",
        background=True
    )

def main():
    """Main startup function"""
    print("🚌 Real-Time Public Transport Monitoring System")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependencies check failed. Please fix the issues above.")
        sys.exit(1)
    
    # Start backend
    if not start_backend():
        print("\n❌ Failed to start backend")
        sys.exit(1)
    
    # Wait for backend to start
    print("\n⏳ Waiting for backend to start...")
    time.sleep(10)
    
    # Start frontend
    if not start_frontend():
        print("\n❌ Failed to start frontend")
        sys.exit(1)
    
    # Start GPS simulator
    if not start_gps_simulator():
        print("\n⚠️  GPS simulator failed to start (this is optional)")
    
    print("\n🎉 System started successfully!")
    print("\n📱 Access the application:")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    
    print("\n🛑 To stop the system:")
    print("   Press Ctrl+C or close this terminal")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down system...")
        print("✅ System stopped")

if __name__ == "__main__":
    main()
