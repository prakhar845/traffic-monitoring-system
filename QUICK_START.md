# 🚀 Quick Start Guide

Get the Traffic Monitoring System running in 5 minutes!

## ⚡ Super Quick Start

### 1. Prerequisites (2 minutes)
```bash
# Check if you have Python 3.8+
python --version

# Check if you have Node.js 14+
node --version

# Check if you have MySQL 8.0+
mysql --version

# Check if you have Redis 6.0+
redis-server --version
```

**Missing something?** See [Prerequisites](#prerequisites) section below.

### 2. One-Command Setup (2 minutes)
```bash
# Run the automated setup
python setup_system.py
```

### 3. Start Services (1 minute)
```bash
# Start MySQL (if not running)
# Windows: net start mysql
# macOS/Linux: sudo systemctl start mysql

# Start Redis (if not running)
# Windows: redis-server
# macOS/Linux: sudo systemctl start redis

# Start the system
python start_working_final.py
```

### 4. Access the Application
- **Complete Demo:** http://localhost:3000/complete_demo.html
- **API Docs:** http://localhost:8000/docs

**That's it! 🎉**

---

## 📋 Prerequisites

### Required Software

| Software | Version | Download Link |
|----------|---------|---------------|
| **Python** | 3.8+ | https://python.org/downloads/ |
| **Node.js** | 14+ | https://nodejs.org/downloads/ |
| **MySQL** | 8.0+ | https://dev.mysql.com/downloads/ |
| **Redis** | 6.0+ | https://redis.io/download |

### Quick Installation

#### Windows
```powershell
# Install Python
# Download from python.org and run installer

# Install Node.js
# Download from nodejs.org and run installer

# Install MySQL
# Download MySQL Installer from dev.mysql.com

# Install Redis
# Download Redis for Windows or use WSL
```

#### macOS
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install all dependencies
brew install python node mysql redis
```

#### Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install all dependencies
sudo apt install python3 python3-pip nodejs npm mysql-server redis-server
```

---

## 🛠️ Manual Setup (If Automated Setup Fails)

### Step 1: Backend Setup
```bash
# Create virtual environment
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Frontend Setup
```bash
# Install Node.js dependencies
cd frontend
npm install
```

### Step 3: Database Setup
```bash
# Start MySQL
sudo systemctl start mysql  # Linux/macOS
# or net start mysql        # Windows

# Start Redis
sudo systemctl start redis  # Linux/macOS
# or redis-server           # Windows

# Setup database
python backend/scripts/setup_database_simple.py
```

### Step 4: Configuration
```bash
# Create .env file in backend directory
cat > backend/.env << EOF
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=traffic_monitoring

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

JWT_SECRET_KEY=your_super_secret_jwt_key_change_this_in_production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

FRONTEND_URL=http://localhost:3000
EOF
```

### Step 5: Start the System
```bash
# Start backend
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
python main_demo.py

# In another terminal, start frontend
cd frontend
npm start

# Or use HTTP server
python -m http.server 3000
```

---

## 🎯 What You'll See

### 1. Real-Time Bus Tracking
- Buses moving on the map every 5 seconds
- Live speed and direction updates
- Route visualization

### 2. Interactive Features
- Click on buses to see details
- Select routes to view their paths
- Real-time arrival predictions

### 3. System Status
- Connection status indicator
- Live system statistics
- Performance metrics

---

## 🔧 Troubleshooting

### Common Issues

#### "MySQL connection failed"
```bash
# Check if MySQL is running
sudo systemctl status mysql

# Start MySQL
sudo systemctl start mysql

# Check credentials in backend/.env
```

#### "Redis connection failed"
```bash
# Check if Redis is running
sudo systemctl status redis

# Start Redis
sudo systemctl start redis
```

#### "Module not found"
```bash
# Activate virtual environment
cd backend
source venv/bin/activate  # macOS/Linux
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

#### "Port already in use"
```bash
# Find process using port
lsof -ti:8000

# Kill process
kill -9 $(lsof -ti:8000)
```

### Get Help
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions
- See [README.md](README.md) for complete documentation
- Run `python setup_system.py` for system diagnostics

---

## 🎉 Success!

If everything is working, you should see:

1. **Backend running** on http://localhost:8000
2. **Frontend running** on http://localhost:3000
3. **Buses moving** on the map in real-time
4. **WebSocket connection** showing live updates

### Next Steps
- Explore the API documentation at http://localhost:8000/docs
- Try the complete demo at http://localhost:3000/complete_demo.html
- Read the full [README.md](README.md) for advanced features

**Happy Monitoring! 🚌✨**
