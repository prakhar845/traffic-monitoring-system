#!/usr/bin/env python3
"""
Generate Super Secret JWT Key
Creates a cryptographically secure JWT secret key
"""

import secrets
import string
import os

def generate_jwt_secret_key():
    """Generate a super secret JWT key"""
    # Generate a 64-character random string with mixed case, numbers, and symbols
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    secret_key = ''.join(secrets.choice(alphabet) for _ in range(64))
    return secret_key

def update_env_file():
    """Update the .env file with the new JWT secret key"""
    secret_key = generate_jwt_secret_key()
    
    env_content = f"""# MySQL Configuration
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
JWT_SECRET_KEY={secret_key}
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
"""
    
    env_file = "backend/.env"
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✅ Updated {env_file} with super secret JWT key")
        print(f"🔐 JWT Secret Key: {secret_key}")
        return True
    except Exception as e:
        print(f"❌ Error updating {env_file}: {e}")
        return False

def main():
    """Main function"""
    print("🔐 Generating Super Secret JWT Key")
    print("=" * 40)
    
    # Generate the secret key
    secret_key = generate_jwt_secret_key()
    print(f"Generated JWT Secret Key: {secret_key}")
    print(f"Key Length: {len(secret_key)} characters")
    print(f"Key Type: Cryptographically secure random string")
    
    # Update .env file
    print("\n📝 Updating .env file...")
    if update_env_file():
        print("\n✅ JWT secret key updated successfully!")
        print("\n🔒 Security Features:")
        print("   - 64-character random string")
        print("   - Mixed case letters, numbers, and symbols")
        print("   - Cryptographically secure generation")
        print("   - Unique for this installation")
        
        print("\n⚠️  IMPORTANT SECURITY NOTES:")
        print("   - Keep this key secret and secure")
        print("   - Never commit this key to version control")
        print("   - Use different keys for different environments")
        print("   - Rotate keys periodically in production")
        
    else:
        print("\n❌ Failed to update .env file")

if __name__ == "__main__":
    main()
