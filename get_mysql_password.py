#!/usr/bin/env python3
"""
Get MySQL Password and Configure System
"""

import mysql.connector
import getpass
import os

def test_mysql_with_password(password):
    """Test MySQL connection with password"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password=password
        )
        print("✅ MySQL connection successful!")
        connection.close()
        return True
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        return False

def update_env_with_password(password):
    """Update .env file with the correct password"""
    env_content = f"""# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD={password}
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
        print(f"✅ Updated {env_file} with correct MySQL password")
        return True
    except Exception as e:
        print(f"❌ Error updating {env_file}: {e}")
        return False

def main():
    """Main function"""
    print("🔐 MySQL Password Configuration")
    print("=" * 40)
    
    # Get MySQL password from user
    password = getpass.getpass("Enter your MySQL root password: ")
    
    # Test connection
    if test_mysql_with_password(password):
        # Update .env file
        if update_env_with_password(password):
            print("\n🎉 Configuration updated successfully!")
            print("🚀 You can now run the production system:")
            print("   python start_production.py")
        else:
            print("\n❌ Failed to update configuration file")
    else:
        print("\n❌ Invalid MySQL password. Please try again.")

if __name__ == "__main__":
    main()
