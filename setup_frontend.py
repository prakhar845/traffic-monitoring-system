#!/usr/bin/env python3
"""
Setup script for the Real-Time Public Transport Monitoring System Frontend
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description, cwd=None):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            cwd=cwd
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_node_version():
    """Check if Node.js is installed and version is compatible"""
    try:
        result = subprocess.run("node --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Node.js version {version} is installed")
            return True
        else:
            print("❌ Node.js is not installed")
            return False
    except:
        print("❌ Node.js is not installed")
        return False

def check_npm_version():
    """Check if npm is installed"""
    try:
        result = subprocess.run("npm --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ npm version {version} is installed")
            return True
        else:
            print("❌ npm is not installed")
            return False
    except:
        print("❌ npm is not installed")
        return False

def install_dependencies():
    """Install npm dependencies"""
    return run_command(
        "npm install",
        "Installing npm dependencies",
        cwd="frontend"
    )

def main():
    """Main setup function"""
    print("🚌 Real-Time Public Transport Monitoring System - Frontend Setup")
    print("=" * 60)
    
    # Check Node.js and npm
    if not check_node_version():
        print("\n📋 Node.js Installation Instructions:")
        print("1. Download Node.js from https://nodejs.org/")
        print("2. Install Node.js (includes npm)")
        print("3. Restart your terminal")
        print("4. Run this setup script again")
        sys.exit(1)
    
    if not check_npm_version():
        print("\n📋 npm Installation Instructions:")
        print("1. npm should be included with Node.js")
        print("2. If not, reinstall Node.js")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    print("\n🎉 Frontend setup completed!")
    print("\n📝 Next steps:")
    print("1. Make sure the backend server is running")
    print("2. Start the frontend development server:")
    print("   cd frontend && npm start")
    print("3. Open http://localhost:3000 in your browser")
    
    print("\n🔗 Useful commands:")
    print("- Start dev server: cd frontend && npm start")
    print("- Build for production: cd frontend && npm run build")
    print("- Run tests: cd frontend && npm test")

if __name__ == "__main__":
    main()
