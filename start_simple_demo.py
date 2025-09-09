#!/usr/bin/env python3
"""
Simple demo startup script for the Real-Time Public Transport Monitoring System
This version uses a simple HTML file instead of React
"""

import os
import sys
import subprocess
import time
import platform
import webbrowser
from pathlib import Path
import http.server
import socketserver
import threading

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

def start_frontend_server():
    """Start a simple HTTP server for the frontend"""
    print("\n🚀 Starting Frontend Server...")
    
    # Check if demo.html exists
    demo_file = Path("frontend/public/demo.html")
    if not demo_file.exists():
        print("❌ Demo HTML file not found")
        return False
    
    # Start HTTP server
    os.chdir("frontend/public")
    
    PORT = 3000
    Handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"✅ Frontend server started on http://localhost:{PORT}")
            print(f"   Demo available at: http://localhost:{PORT}/demo.html")
            
            # Start server in a separate thread
            server_thread = threading.Thread(target=httpd.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            
            return True
    except Exception as e:
        print(f"❌ Failed to start frontend server: {e}")
        return False

def main():
    """Main startup function"""
    print("🚌 Real-Time Public Transport Monitoring System - SIMPLE DEMO")
    print("=" * 70)
    print("⚠️  This is a simple demo version using HTML instead of React")
    print("   For full functionality, please set up the complete system")
    
    # Start backend
    if not start_backend():
        print("\n❌ Failed to start backend")
        sys.exit(1)
    
    # Wait for backend to start
    print("\n⏳ Waiting for backend to start...")
    time.sleep(10)
    
    # Start frontend server
    if not start_frontend_server():
        print("\n❌ Failed to start frontend server")
        sys.exit(1)
    
    print("\n🎉 Simple demo system started successfully!")
    print("\n📱 Access the application:")
    print("   Demo: http://localhost:3000/demo.html")
    print("   Backend API: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    
    print("\n⚠️  Note: This simple demo version has limited functionality")
    print("   - No interactive map (placeholder only)")
    print("   - Basic HTML interface")
    print("   - Real-time WebSocket updates")
    print("   - Simulated bus data")
    
    # Try to open browser
    try:
        webbrowser.open('http://localhost:3000/demo.html')
        print("\n🌐 Opening demo in your default browser...")
    except:
        print("\n🌐 Please open http://localhost:3000/demo.html in your browser")
    
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
