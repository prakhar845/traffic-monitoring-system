#!/usr/bin/env python3
"""
Demo startup script for the Real-Time Public Transport Monitoring System
This version works without MySQL and Redis for demonstration purposes
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

def start_backend():
    """Start the backend server"""
    print("\n🚀 Starting Backend Server...")
    
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
    return run_command(
        f"{python_cmd} main_demo.py",
        "Starting FastAPI demo backend server",
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

def main():
    """Main startup function"""
    print("🚌 Real-Time Public Transport Monitoring System - DEMO")
    print("=" * 60)
    print("⚠️  This is a demo version that works without MySQL/Redis")
    print("   For full functionality, please set up MySQL and Redis")
    
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
    
    print("\n🎉 Demo system started successfully!")
    print("\n📱 Access the application:")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    
    print("\n⚠️  Note: This demo version has limited functionality")
    print("   - No database persistence")
    print("   - No Redis caching")
    print("   - Simulated data only")
    
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
