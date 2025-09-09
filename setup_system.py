#!/usr/bin/env python3
"""
Automated System Setup Script
Sets up the complete Traffic Monitoring System on any machine
"""

import os
import sys
import subprocess
import platform
import time
from pathlib import Path

def print_header():
    """Print setup header"""
    print("🚌 Real-Time Public Transport Monitoring System - Setup")
    print("=" * 60)
    print("This script will set up the complete system on your machine")
    print("=" * 60)

def check_python():
    """Check Python installation"""
    print("\n🐍 Checking Python installation...")
    try:
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print(f"❌ Python {version.major}.{version.minor} found. Python 3.8+ required.")
            return False
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} found")
        return True
    except Exception as e:
        print(f"❌ Python check failed: {e}")
        return False

def check_node():
    """Check Node.js installation"""
    print("\n📦 Checking Node.js installation...")
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()} found")
            return True
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found")
        return False

def check_mysql():
    """Check MySQL installation"""
    print("\n🗄️ Checking MySQL installation...")
    try:
        result = subprocess.run(["mysql", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ MySQL found: {result.stdout.strip()}")
            return True
        else:
            print("❌ MySQL not found")
            return False
    except FileNotFoundError:
        print("❌ MySQL not found")
        return False

def check_redis():
    """Check Redis installation"""
    print("\n⚡ Checking Redis installation...")
    try:
        result = subprocess.run(["redis-server", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Redis found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Redis not found")
            return False
    except FileNotFoundError:
        print("❌ Redis not found")
        return False

def install_python_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    try:
        # Create virtual environment
        venv_path = Path("backend/venv")
        if not venv_path.exists():
            subprocess.run([sys.executable, "-m", "venv", "backend/venv"], check=True)
            print("✅ Virtual environment created")
        
        # Get pip command
        if platform.system() == "Windows":
            pip_cmd = "backend\\venv\\Scripts\\pip.exe"
        else:
            pip_cmd = "backend/venv/bin/pip"
        
        # Install requirements
        subprocess.run([pip_cmd, "install", "-r", "backend/requirements.txt"], check=True)
        print("✅ Python dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False

def install_node_dependencies():
    """Install Node.js dependencies"""
    print("\n📦 Installing Node.js dependencies...")
    try:
        subprocess.run(["npm", "install"], cwd="frontend", check=True)
        print("✅ Node.js dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Node.js dependencies: {e}")
        return False

def setup_environment():
    """Setup environment variables"""
    print("\n⚙️ Setting up environment configuration...")
    try:
        env_file = Path("backend/.env")
        if not env_file.exists():
            # Create default .env file
            env_content = """# Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=traffic_monitoring

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# JWT Configuration
JWT_SECRET_KEY=your_super_secret_jwt_key_change_this_in_production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Frontend Configuration
FRONTEND_URL=http://localhost:3000
"""
            env_file.write_text(env_content)
            print("✅ Environment file created")
        else:
            print("✅ Environment file already exists")
        return True
    except Exception as e:
        print(f"❌ Failed to setup environment: {e}")
        return False

def setup_database():
    """Setup database"""
    print("\n🗄️ Setting up database...")
    try:
        # Get python command
        if platform.system() == "Windows":
            python_cmd = "backend\\venv\\Scripts\\python.exe"
        else:
            python_cmd = "backend/venv/bin/python"
        
        # Run database setup
        subprocess.run([python_cmd, "backend/scripts/setup_database_simple.py"], check=True)
        print("✅ Database setup completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Database setup failed: {e}")
        return False

def create_startup_scripts():
    """Create convenient startup scripts"""
    print("\n📝 Creating startup scripts...")
    try:
        # Windows batch file
        windows_script = """@echo off
echo Starting Traffic Monitoring System...
python start_working_final.py
pause
"""
        Path("start_system.bat").write_text(windows_script)
        
        # Unix shell script
        unix_script = """#!/bin/bash
echo "Starting Traffic Monitoring System..."
python3 start_working_final.py
"""
        unix_file = Path("start_system.sh")
        unix_file.write_text(unix_script)
        unix_file.chmod(0o755)
        
        print("✅ Startup scripts created")
        return True
    except Exception as e:
        print(f"❌ Failed to create startup scripts: {e}")
        return False

def print_instructions():
    """Print post-installation instructions"""
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Start MySQL service:")
    if platform.system() == "Windows":
        print("   - Open Command Prompt as Administrator")
        print("   - Run: net start mysql")
    else:
        print("   - Run: sudo systemctl start mysql")
    
    print("\n2. Start Redis service:")
    if platform.system() == "Windows":
        print("   - Run: redis-server")
    else:
        print("   - Run: sudo systemctl start redis")
    
    print("\n3. Start the system:")
    print("   - Run: python start_working_final.py")
    print("   - Or use: start_system.bat (Windows) / ./start_system.sh (Unix)")
    
    print("\n4. Access the application:")
    print("   - Complete Demo: http://localhost:3000/complete_demo.html")
    print("   - Working Demo: http://localhost:3000/working_demo.html")
    print("   - API Documentation: http://localhost:8000/docs")
    
    print("\n📚 For detailed instructions, see README.md")
    print("\n🆘 If you encounter issues:")
    print("   - Check the troubleshooting section in README.md")
    print("   - Ensure MySQL and Redis are running")
    print("   - Verify your .env file configuration")

def main():
    """Main setup function"""
    print_header()
    
    # Check prerequisites
    if not check_python():
        print("\n❌ Python 3.8+ is required. Please install Python and try again.")
        return False
    
    if not check_node():
        print("\n⚠️ Node.js not found. Frontend features may not work.")
        print("   Please install Node.js 14+ from https://nodejs.org/")
    
    if not check_mysql():
        print("\n⚠️ MySQL not found. Database features will not work.")
        print("   Please install MySQL 8.0+ from https://dev.mysql.com/downloads/")
    
    if not check_redis():
        print("\n⚠️ Redis not found. Caching features will not work.")
        print("   Please install Redis 6.0+ from https://redis.io/download/")
    
    # Install dependencies
    if not install_python_dependencies():
        print("\n❌ Failed to install Python dependencies")
        return False
    
    if not install_node_dependencies():
        print("\n⚠️ Failed to install Node.js dependencies")
    
    # Setup configuration
    if not setup_environment():
        print("\n❌ Failed to setup environment")
        return False
    
    # Setup database (only if MySQL is available)
    if check_mysql():
        if not setup_database():
            print("\n⚠️ Database setup failed. You may need to configure MySQL manually.")
    
    # Create startup scripts
    create_startup_scripts()
    
    # Print instructions
    print_instructions()
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup failed. Please check the errors above and try again.")
        sys.exit(1)
    else:
        print("\n✅ Setup completed successfully!")
        sys.exit(0)
