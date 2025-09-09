# 🚌 Real-Time Public Transport Monitoring and Prediction System

A comprehensive, full-stack data science application for monitoring public transport in real-time with ML-powered predictions, analytics, and interactive mapping.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Usage Guide](#usage-guide)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

This system provides real-time monitoring of public transport with advanced features including:

- **Real-time GPS tracking** of buses with live location updates
- **ML-powered arrival predictions** using time-series analysis
- **Interactive web interface** with live maps and analytics
- **WebSocket streaming** for real-time data updates
- **User authentication** and role-based access control
- **Traffic condition monitoring** and analysis
- **Comprehensive analytics** dashboard
- **Production-ready** database and caching

## ✨ Features

### Core Features
- 🚌 **Real-time Bus Tracking** - Live GPS tracking with 5-second updates
- 🗺️ **Interactive Maps** - Leaflet-based maps with route visualization
- 🤖 **ML Predictions** - Arrival time predictions using Random Forest models
- 📊 **Analytics Dashboard** - Performance metrics and system monitoring
- 🔐 **User Authentication** - JWT-based authentication with role management
- 🌐 **WebSocket Streaming** - Real-time data updates to connected clients
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile devices

### Advanced Features
- 🚦 **Traffic Monitoring** - Real-time traffic condition analysis
- 📈 **Performance Analytics** - Route efficiency and bus performance metrics
- 🔄 **Auto-recovery** - Automatic process monitoring and restart
- 💾 **Data Persistence** - MySQL database with full schema
- ⚡ **High Performance** - Redis caching for optimal performance
- 🛡️ **Error Handling** - Comprehensive error handling and logging

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (React/HTML)  │◄──►│   (FastAPI)     │◄──►│   (MySQL)       │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 3306    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │   Redis Cache   │              │
         │              │   Port: 6379    │              │
         │              └─────────────────┘              │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   ML Models     │
                    │   (Scikit-learn)│
                    └─────────────────┘
```

### Technology Stack

**Backend:**
- Python 3.8+
- FastAPI (Web framework)
- SQLAlchemy (ORM)
- MySQL (Database)
- Redis (Caching)
- WebSockets (Real-time communication)
- Scikit-learn (ML models)

**Frontend:**
- React.js (Optional)
- HTML5/CSS3/JavaScript
- Leaflet (Maps)
- WebSocket API

**Infrastructure:**
- Docker (Optional)
- Nginx (Optional)
- Uvicorn (ASGI server)

## 📋 Prerequisites

### System Requirements
- **Operating System:** Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **RAM:** Minimum 4GB, Recommended 8GB+
- **Storage:** At least 2GB free space
- **Network:** Internet connection for map tiles and package downloads

### Software Dependencies

#### Required Software
1. **Python 3.8 or higher**
   ```bash
   # Check Python version
   python --version
   # or
   python3 --version
   ```

2. **Node.js 14+ and npm**
   ```bash
   # Check Node.js version
   node --version
   # Check npm version
   npm --version
   ```

3. **MySQL 8.0+**
   - Download from: https://dev.mysql.com/downloads/
   - Or use package manager:
     ```bash
     # Ubuntu/Debian
     sudo apt-get install mysql-server
     
     # macOS (with Homebrew)
     brew install mysql
     
     # Windows
     # Download MySQL Installer from official website
     ```

4. **Redis 6.0+**
   - Download from: https://redis.io/download
   - Or use package manager:
     ```bash
     # Ubuntu/Debian
     sudo apt-get install redis-server
     
     # macOS (with Homebrew)
     brew install redis
     
     # Windows
     # Download Redis for Windows or use WSL
     ```

#### Optional Software
- **Git** (for version control)
- **Docker** (for containerized deployment)
- **Postman** (for API testing)

## 🚀 Installation

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone <repository-url>
cd traffic-monitoring-system

# Or download and extract the ZIP file
```

### Step 2: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 3: Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install
```

### Step 4: Database Setup

1. **Start MySQL service:**
   ```bash
   # Windows (as Administrator)
   net start mysql
   
   # macOS/Linux
   sudo systemctl start mysql
   # or
   sudo service mysql start
   ```

2. **Start Redis service:**
   ```bash
   # Windows
   redis-server
   
   # macOS/Linux
   sudo systemctl start redis
   # or
   sudo service redis start
   ```

3. **Configure database:**
   ```bash
   # Run database setup script
   python backend/scripts/setup_database_simple.py
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
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
JWT_SECRET_KEY=your_super_secret_jwt_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Frontend Configuration
FRONTEND_URL=http://localhost:3000
```

### MySQL Configuration

1. **Create database user (optional):**
   ```sql
   CREATE USER 'traffic_user'@'localhost' IDENTIFIED BY 'secure_password';
   GRANT ALL PRIVILEGES ON traffic_monitoring.* TO 'traffic_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

2. **Update .env file with new credentials if using custom user**

### Redis Configuration

1. **Configure Redis (optional):**
   ```bash
   # Edit Redis configuration
   sudo nano /etc/redis/redis.conf
   
   # Set password (optional)
   requirepass your_redis_password
   
   # Restart Redis
   sudo systemctl restart redis
   ```

2. **Update .env file with Redis password if set**

## 🏃‍♂️ Running the Application

### Quick Start (Recommended)

```bash
# Run the complete system
python start_working_final.py
```

This will:
- Check all dependencies
- Set up the database
- Start the backend server
- Start the frontend server
- Display access URLs

### Manual Start

#### Option 1: Backend Only
```bash
# Activate virtual environment
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Start backend
python main_demo.py
```

#### Option 2: Frontend Only
```bash
# Start frontend
cd frontend
npm start
```

#### Option 3: HTTP Server (for demos)
```bash
# Start HTTP server
python -m http.server 3000
```

### Production Deployment

```bash
# Run production system
python start_complete_system.py
```

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Interactive Documentation
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Key Endpoints

#### System
- `GET /` - System information
- `GET /health` - Health check
- `WebSocket /ws/live-updates` - Real-time updates

#### Routes
- `GET /api/routes/` - Get all routes
- `GET /api/routes/{id}` - Get specific route

#### Buses
- `GET /api/buses/` - Get all buses with locations
- `GET /api/buses/{id}` - Get specific bus

#### Stops
- `GET /api/stops/` - Get all stops

#### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Get current user

#### Analytics
- `GET /api/analytics/overview` - System overview
- `GET /api/analytics/routes` - Route analytics
- `GET /api/analytics/performance` - Performance metrics

### Example API Usage

```bash
# Get all routes
curl http://localhost:8000/api/routes/

# Get all buses
curl http://localhost:8000/api/buses/

# Health check
curl http://localhost:8000/health
```

## 📖 Usage Guide

### Accessing the Application

1. **Complete Demo:** http://localhost:3000/complete_demo.html
2. **Working Demo:** http://localhost:3000/working_demo.html
3. **API Documentation:** http://localhost:8000/docs

### Default Credentials

- **Username:** admin
- **Password:** admin123

### Using the Interface

1. **View Routes:** Click on route cards to see route details
2. **Track Buses:** Watch buses move in real-time on the map
3. **Check Predictions:** View arrival time predictions for stops
4. **Monitor Analytics:** Access analytics dashboard (admin users)

### WebSocket Connection

The system uses WebSockets for real-time updates. Connect to:
```
ws://localhost:8000/ws/live-updates
```

## 🔧 Troubleshooting

### Common Issues

#### 1. MySQL Connection Failed
```
Error: 1045 (28000): Access denied for user 'root'@'localhost'
```
**Solution:**
- Check MySQL is running: `sudo systemctl status mysql`
- Verify credentials in `.env` file
- Reset MySQL password if needed

#### 2. Redis Connection Failed
```
Error: AUTH <password> called without any password configured
```
**Solution:**
- Check Redis is running: `sudo systemctl status redis`
- Verify Redis configuration
- Set `REDIS_PASSWORD=` in `.env` if no password

#### 3. Port Already in Use
```
Error: [Errno 48] Address already in use
```
**Solution:**
- Kill process using port: `lsof -ti:8000 | xargs kill -9`
- Change port in configuration
- Restart the service

#### 4. Module Not Found
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution:**
- Activate virtual environment
- Install dependencies: `pip install -r requirements.txt`
- Check Python path

#### 5. Frontend Build Errors
```
Error: Cannot find module './typeof'
```
**Solution:**
- Clear node_modules: `rm -rf node_modules package-lock.json`
- Reinstall: `npm install`
- Use HTTP server demo as fallback

### Debug Mode

Enable debug mode for detailed logging:
```env
DEBUG=True
```

### Logs

Check logs for detailed error information:
- **Backend logs:** `traffic_monitoring.log`
- **System logs:** `system_startup.log`

## 🛠️ Development

### Project Structure

```
traffic-monitoring-system/
├── backend/
│   ├── database/          # Database models and connections
│   ├── routers/           # API route handlers
│   ├── services/          # Business logic and ML models
│   ├── scripts/           # Database setup and utilities
│   ├── main_demo.py       # Demo backend server
│   ├── main_complete.py   # Complete backend server
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/               # React source code
│   ├── public/            # Static assets
│   ├── package.json       # Node.js dependencies
│   └── App_complete.js    # Complete React app
├── complete_demo.html     # Complete HTML demo
├── working_demo.html      # Working HTML demo
├── start_working_final.py # Main startup script
└── README.md             # This file
```

### Adding New Features

1. **Backend API:**
   - Add routes in `backend/routers/`
   - Implement business logic in `backend/services/`
   - Update database models if needed

2. **Frontend:**
   - Modify React components in `frontend/src/`
   - Update HTML demos for quick testing
   - Add new API calls

3. **Database:**
   - Update models in `backend/database/models.py`
   - Create migration scripts
   - Update setup scripts

### Testing

```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests
cd frontend
npm test

# Integration tests
python test_integration.py
```

### Code Quality

```bash
# Python formatting
black backend/
isort backend/

# JavaScript formatting
cd frontend
npm run format

# Linting
cd frontend
npm run lint
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use meaningful commit messages
- Add tests for new features
- Update documentation
- Test on multiple platforms

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help

1. **Check the documentation** - Most issues are covered here
2. **Review troubleshooting section** - Common solutions provided
3. **Check logs** - Detailed error information available
4. **Create an issue** - For bugs and feature requests

### Contact

- **Issues:** Create a GitHub issue
- **Discussions:** Use GitHub Discussions
- **Email:** [Your email here]

## 🎉 Acknowledgments

- **FastAPI** - Modern, fast web framework
- **Leaflet** - Open-source mapping library
- **React** - Frontend framework
- **MySQL** - Database management system
- **Redis** - In-memory data store
- **Scikit-learn** - Machine learning library

---

**Happy Monitoring! 🚌✨**

*Built with ❤️ for better public transport*