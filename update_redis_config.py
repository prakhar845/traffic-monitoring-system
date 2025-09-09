#!/usr/bin/env python3
"""
Update Redis Configuration
"""

import os

def update_redis_config():
    """Update .env file to fix Redis configuration"""
    env_content = """# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=traffic_monitoring

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# Security Configuration
JWT_SECRET_KEY=(=A$^5M+<-;g1#G9H*bZqtSK<js$5%t*wL)4qGxC;w(Zo,0A(9panFJ)ZISCcbiP
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
"""
    
    env_file = "backend/.env"
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✅ Updated {env_file} with fixed Redis configuration")
        return True
    except Exception as e:
        print(f"❌ Error updating {env_file}: {e}")
        return False

if __name__ == "__main__":
    update_redis_config()
