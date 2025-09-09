#!/usr/bin/env python3
"""
Test Environment Loading Script
"""

import os
from dotenv import load_dotenv

# Load environment variables from backend directory
load_dotenv("backend/.env")

print("🔍 Testing environment variable loading...")
print(f"MYSQL_HOST: {os.getenv('MYSQL_HOST', 'NOT_FOUND')}")
print(f"MYSQL_PORT: {os.getenv('MYSQL_PORT', 'NOT_FOUND')}")
print(f"MYSQL_USER: {os.getenv('MYSQL_USER', 'NOT_FOUND')}")
print(f"MYSQL_PASSWORD: {'***' if os.getenv('MYSQL_PASSWORD') else 'EMPTY'}")
print(f"MYSQL_DATABASE: {os.getenv('MYSQL_DATABASE', 'NOT_FOUND')}")

# Test MySQL connection
import mysql.connector

try:
    connection = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        port=int(os.getenv('MYSQL_PORT', '3306')),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', '')
    )
    print("✅ MySQL connection successful!")
    connection.close()
except Exception as e:
    print(f"❌ MySQL connection failed: {e}")
