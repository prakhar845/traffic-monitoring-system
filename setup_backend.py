#!/usr/bin/env python3
"""
Setup script for the Real-Time Public Transport Monitoring System Backend
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def create_virtual_environment():
    """Create virtual environment"""
    venv_path = Path("backend/venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    return run_command(
        f"python -m venv {venv_path}",
        "Creating virtual environment"
    )

def get_activation_command():
    """Get the correct activation command based on OS"""
    if platform.system() == "Windows":
        return "backend\\venv\\Scripts\\activate"
    else:
        return "source backend/venv/bin/activate"

def install_dependencies():
    """Install Python dependencies"""
    if platform.system() == "Windows":
        pip_command = "backend\\venv\\Scripts\\pip"
    else:
        pip_command = "backend/venv/bin/pip"
    
    return run_command(
        f"{pip_command} install -r backend/requirements.txt",
        "Installing Python dependencies"
    )

def create_env_file():
    """Create .env file from example"""
    env_file = Path("backend/.env")
    env_example = Path("backend/env_example.txt")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if env_example.exists():
        # Copy example to .env
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ Created .env file from example")
        print("⚠️  Please update the database credentials in backend/.env")
        return True
    else:
        print("❌ env_example.txt not found")
        return False

def setup_database():
    """Setup database (MySQL)"""
    print("\n📋 Database Setup Instructions:")
    print("1. Install MySQL Server")
    print("2. Create a database named 'traffic_monitoring'")
    print("3. Update the database credentials in backend/.env")
    print("4. The application will automatically create tables on first run")
    
    return True

def setup_redis():
    """Setup Redis"""
    print("\n📋 Redis Setup Instructions:")
    print("1. Install Redis Server")
    print("2. Start Redis server")
    print("3. Update Redis credentials in backend/.env if needed")
    
    return True

def main():
    """Main setup function"""
    print("🚌 Real-Time Public Transport Monitoring System - Backend Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        sys.exit(1)
    
    # Setup instructions
    setup_database()
    setup_redis()
    
    print("\n🎉 Backend setup completed!")
    print("\n📝 Next steps:")
    print("1. Install and configure MySQL and Redis")
    print("2. Update backend/.env with your database credentials")
    print("3. Activate the virtual environment:")
    print(f"   {get_activation_command()}")
    print("4. Run the backend server:")
    print("   cd backend && python main.py")
    
    print("\n🔗 Useful commands:")
    print("- Activate venv:", get_activation_command())
    print("- Run backend: cd backend && python main.py")
    print("- Install new package: pip install package_name")

if __name__ == "__main__":
    main()
