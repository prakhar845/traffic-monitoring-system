#!/usr/bin/env python3
"""
Environment Setup Script
Creates the .env file with correct MySQL configuration
"""

import os

def create_env_file():
    """Create the .env file with correct configuration"""
    env_content = """# MySQL Configuration
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

# Security Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
"""
    
    env_file = "backend/.env"
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✅ Created {env_file} with correct configuration")
        return True
    except Exception as e:
        print(f"❌ Error creating {env_file}: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Setting up environment configuration...")
    
    if create_env_file():
        print("✅ Environment setup completed!")
        print("\n🚀 You can now run the production system:")
        print("   python start_production.py")
    else:
        print("❌ Environment setup failed")

if __name__ == "__main__":
    main()
