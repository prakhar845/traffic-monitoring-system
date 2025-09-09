# 🔧 Troubleshooting Guide

This guide helps you resolve common issues when setting up and running the Traffic Monitoring System.

## 📋 Quick Diagnostics

### System Check Script
Run this to check your system status:
```bash
python setup_system.py
```

### Manual Checks
```bash
# Check Python
python --version

# Check Node.js
node --version

# Check MySQL
mysql --version

# Check Redis
redis-server --version
```

## 🚨 Common Issues and Solutions

### 1. MySQL Connection Issues

#### Error: `1045 (28000): Access denied for user 'root'@'localhost'`

**Causes:**
- Wrong password in `.env` file
- MySQL not running
- User doesn't exist

**Solutions:**

1. **Check MySQL is running:**
   ```bash
   # Windows
   net start mysql
   
   # macOS/Linux
   sudo systemctl start mysql
   # or
   sudo service mysql start
   ```

2. **Reset MySQL root password:**
   ```bash
   # Stop MySQL
   sudo systemctl stop mysql
   
   # Start in safe mode
   sudo mysqld_safe --skip-grant-tables &
   
   # Connect and reset password
   mysql -u root
   USE mysql;
   UPDATE user SET authentication_string=PASSWORD('newpassword') WHERE User='root';
   FLUSH PRIVILEGES;
   EXIT;
   
   # Restart MySQL
   sudo systemctl restart mysql
   ```

3. **Update .env file:**
   ```env
   MYSQL_PASSWORD=your_actual_password
   ```

4. **Create new user (alternative):**
   ```sql
   CREATE USER 'traffic_user'@'localhost' IDENTIFIED BY 'secure_password';
   GRANT ALL PRIVILEGES ON traffic_monitoring.* TO 'traffic_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

#### Error: `Can't connect to MySQL server on 'localhost'`

**Solutions:**
1. **Check if MySQL is installed:**
   ```bash
   which mysql
   # or
   where mysql
   ```

2. **Install MySQL:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install mysql-server
   
   # macOS
   brew install mysql
   
   # Windows
   # Download from https://dev.mysql.com/downloads/
   ```

3. **Start MySQL service:**
   ```bash
   # Ubuntu/Debian
   sudo systemctl start mysql
   sudo systemctl enable mysql
   
   # macOS
   brew services start mysql
   ```

### 2. Redis Connection Issues

#### Error: `AUTH <password> called without any password configured`

**Solutions:**
1. **Check Redis configuration:**
   ```bash
   # Check if Redis is running
   redis-cli ping
   ```

2. **Update .env file:**
   ```env
   REDIS_PASSWORD=
   ```

3. **Configure Redis password (if needed):**
   ```bash
   # Edit Redis config
   sudo nano /etc/redis/redis.conf
   
   # Add password
   requirepass your_redis_password
   
   # Restart Redis
   sudo systemctl restart redis
   ```

#### Error: `Connection refused`

**Solutions:**
1. **Start Redis:**
   ```bash
   # Ubuntu/Debian
   sudo systemctl start redis
   
   # macOS
   brew services start redis
   
   # Windows
   redis-server
   ```

2. **Check Redis port:**
   ```bash
   netstat -tlnp | grep 6379
   ```

### 3. Python Environment Issues

#### Error: `ModuleNotFoundError: No module named 'fastapi'`

**Solutions:**
1. **Activate virtual environment:**
   ```bash
   # Windows
   backend\venv\Scripts\activate
   
   # macOS/Linux
   source backend/venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Check Python path:**
   ```bash
   which python
   pip list
   ```

#### Error: `The module 'venv' could not be loaded`

**Solutions:**
1. **Recreate virtual environment:**
   ```bash
   rm -rf backend/venv
   python -m venv backend/venv
   ```

2. **Use system Python:**
   ```bash
   pip install -r backend/requirements.txt
   ```

### 4. Node.js Issues

#### Error: `Cannot find module './typeof'`

**Solutions:**
1. **Clear and reinstall:**
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Update Node.js:**
   ```bash
   # Check version
   node --version
   
   # Update if needed
   # Download from https://nodejs.org/
   ```

3. **Use HTTP server fallback:**
   ```bash
   python -m http.server 3000
   ```

#### Error: `npm error code ENOENT`

**Solutions:**
1. **Check if in correct directory:**
   ```bash
   pwd
   ls package.json
   ```

2. **Navigate to frontend directory:**
   ```bash
   cd frontend
   npm install
   ```

### 5. Port Issues

#### Error: `[Errno 48] Address already in use`

**Solutions:**
1. **Find process using port:**
   ```bash
   # Find process on port 8000
   lsof -ti:8000
   
   # Kill process
   kill -9 $(lsof -ti:8000)
   ```

2. **Change port:**
   ```bash
   # Update .env file
   API_PORT=8001
   
   # Or use different port
   uvicorn main_demo:app --port 8001
   ```

3. **Check all ports:**
   ```bash
   netstat -tlnp | grep :8000
   netstat -tlnp | grep :3000
   ```

### 6. WebSocket Issues

#### Error: `WebSocket connection failed`

**Solutions:**
1. **Check backend is running:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check WebSocket endpoint:**
   ```bash
   curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Sec-WebSocket-Key: test" -H "Sec-WebSocket-Version: 13" http://localhost:8000/ws/live-updates
   ```

3. **Check firewall settings:**
   ```bash
   # Ubuntu/Debian
   sudo ufw status
   sudo ufw allow 8000
   ```

### 7. Database Schema Issues

#### Error: `Table 'traffic_monitoring.routes' doesn't exist`

**Solutions:**
1. **Run database setup:**
   ```bash
   python backend/scripts/setup_database_simple.py
   ```

2. **Check database exists:**
   ```sql
   SHOW DATABASES;
   USE traffic_monitoring;
   SHOW TABLES;
   ```

3. **Manual table creation:**
   ```sql
   CREATE DATABASE IF NOT EXISTS traffic_monitoring;
   USE traffic_monitoring;
   -- Run the SQL from setup_database_simple.py
   ```

### 8. Permission Issues

#### Error: `Permission denied`

**Solutions:**
1. **Check file permissions:**
   ```bash
   ls -la
   chmod +x start_system.sh
   ```

2. **Run as administrator (Windows):**
   ```cmd
   # Right-click Command Prompt -> Run as Administrator
   ```

3. **Use sudo (Linux/macOS):**
   ```bash
   sudo python start_working_final.py
   ```

## 🔍 Debug Mode

### Enable Debug Logging

1. **Update .env file:**
   ```env
   DEBUG=True
   ```

2. **Check logs:**
   ```bash
   # Backend logs
   tail -f traffic_monitoring.log
   
   # System logs
   tail -f system_startup.log
   ```

### Verbose Output

```bash
# Run with verbose output
python -u start_working_final.py

# Check specific service
curl -v http://localhost:8000/health
```

## 🧪 Testing Components

### Test Database Connection
```python
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv("backend/.env")

try:
    connection = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        port=int(os.getenv('MYSQL_PORT', '3306')),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', '')
    )
    print("✅ MySQL connection successful")
    connection.close()
except Exception as e:
    print(f"❌ MySQL connection failed: {e}")
```

### Test Redis Connection
```python
import redis
from dotenv import load_dotenv
import os

load_dotenv("backend/.env")

try:
    r = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', '6379')),
        password=os.getenv('REDIS_PASSWORD', '') if os.getenv('REDIS_PASSWORD', '') else None
    )
    r.ping()
    print("✅ Redis connection successful")
except Exception as e:
    print(f"❌ Redis connection failed: {e}")
```

### Test API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Routes
curl http://localhost:8000/api/routes/

# Buses
curl http://localhost:8000/api/buses/
```

## 📞 Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide**
2. **Run the system check script**
3. **Check the logs for error details**
4. **Verify all prerequisites are installed**

### When Reporting Issues

Include the following information:

1. **Operating System and version**
2. **Python version**: `python --version`
3. **Node.js version**: `node --version`
4. **MySQL version**: `mysql --version`
5. **Redis version**: `redis-server --version`
6. **Error message (full text)**
7. **Steps to reproduce**
8. **Log files** (if available)

### Useful Commands for Debugging

```bash
# Check all services
systemctl status mysql redis

# Check ports
netstat -tlnp | grep -E ':(3000|8000|3306|6379)'

# Check processes
ps aux | grep -E '(python|node|mysql|redis)'

# Check disk space
df -h

# Check memory
free -h
```

## 🎯 Quick Fixes

### Complete Reset
```bash
# Stop all services
sudo systemctl stop mysql redis

# Remove virtual environment
rm -rf backend/venv

# Remove node modules
rm -rf frontend/node_modules

# Reinstall everything
python setup_system.py
```

### Minimal Working Setup
```bash
# Just run the demo without database
python -m http.server 3000
# In another terminal
cd backend && python main_demo.py
```

### Production Issues
```bash
# Check system resources
htop
df -h
free -h

# Check service logs
journalctl -u mysql
journalctl -u redis

# Restart services
sudo systemctl restart mysql redis
```

---

**Still having issues?** Check the main README.md for more detailed instructions or create an issue with the information requested above.
