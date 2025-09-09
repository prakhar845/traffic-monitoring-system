#!/usr/bin/env python3
"""
Direct MySQL Connection Test
"""

import mysql.connector

def test_mysql_direct():
    """Test MySQL connection directly"""
    try:
        # Test with no password
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password=''
        )
        print("✅ MySQL connection successful with no password!")
        connection.close()
        return True
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        return False

if __name__ == "__main__":
    test_mysql_direct()
