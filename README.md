# BasicWebServer - Anonymous Forum

A simple, single-threaded anonymous forum web application built with Flask and PostgreSQL. This application allows users on the same LAN to connect, read comments, and post their own thoughts without requiring login or sign-up.

## 🌟 Features

- **Anonymous Access**: No login or registration required
- **Real-time Forum**: View and post comments chronologically (oldest at top, newest at bottom)
- **LAN Support**: Accessible to all users on the same local network
- **Docker Support**: Easy deployment on Windows and Linux using Docker
- **PostgreSQL Database**: Reliable data persistence
- **Responsive Frontend**: Clean, modern UI that works on desktop and mobile
- **RESTful API**: JSON API endpoints for programmatic access
- **Health Monitoring**: Built-in health check endpoint

## 📋 Prerequisites

### For Docker Deployment (Recommended)
- Docker Engine 20.10 or higher
- Docker Compose 2.0 or higher

### For Local Development
- Python 3.11 or higher
- PostgreSQL 15 or higher
- pip (Python package manager)

## 🚀 Quick Start with Docker

### 1. Clone the Repository
```bash
git clone https://github.com/VictoKu1/BasicWebServer.git
cd BasicWebServer
```

### 2. Deploy with Docker Compose
```bash
docker-compose up -d
```

This will:
- Build the Flask application container
- Pull and start PostgreSQL database container
- Initialize the database with the required schema
- Start the web server on port 5000

### 3. Access the Forum
Open your web browser and navigate to:
- **On the host machine**: http://localhost:5000
- **From other LAN devices**: http://[HOST_IP]:5000

To find your host IP:
- **Windows**: Run `ipconfig` in Command Prompt, look for IPv4 Address
- **Linux**: Run `ip addr show` or `hostname -I`

### 4. Stop the Application
```bash
docker-compose down
```

To also remove the database volume:
```bash
docker-compose down -v
```

## 🔧 Configuration

### Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` to customize:
```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=postgresql://forumuser:forumpass@db:5432/forumdb

# Server Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

### Docker Compose Configuration

Edit `docker-compose.yml` to customize:
- Database credentials
- Port mappings
- Volume locations
- Network settings

## 🧪 Testing

### Running Tests with Docker

```bash
# Build the test environment
docker-compose build

# Run tests in a temporary container
docker-compose run --rm web python -m pytest tests/ -v
```

### Running Tests Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run tests:
```bash
pytest tests/ -v
```

3. Run tests with coverage:
```bash
pytest tests/ -v --cov=app --cov-report=html
```

### Test Coverage

The test suite includes:
- ✅ Route testing (GET/POST endpoints)
- ✅ API endpoint testing
- ✅ Database model testing
- ✅ Input validation testing
- ✅ Error handling testing
- ✅ Health check testing

## 📖 API Documentation

### Get All Comments
```http
GET /api/comments
```

**Response:**
```json
[
  {
    "id": 1,
    "content": "This is a comment",
    "created_at": "2024-01-01 12:00:00"
  }
]
```

### Post a Comment
```http
POST /api/comments
Content-Type: application/json

{
  "content": "Your comment here"
}
```

**Response:**
```json
{
  "id": 2,
  "content": "Your comment here",
  "created_at": "2024-01-01 12:01:00"
}
```

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

## 🖥️ Local Development Setup

### 1. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Windows:**
Download and install from [PostgreSQL official website](https://www.postgresql.org/download/windows/)

### 2. Create Database

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE forumdb;
CREATE USER forumuser WITH PASSWORD 'forumpass';
GRANT ALL PRIVILEGES ON DATABASE forumdb TO forumuser;
\q
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables

```bash
export DATABASE_URL="postgresql://forumuser:forumpass@localhost:5432/forumdb"
export FLASK_HOST="0.0.0.0"
export FLASK_PORT="5000"
```

### 5. Run the Application

```bash
python -m app.app
```

## 🌐 Network Configuration for LAN Access

### Windows

1. **Allow through Windows Firewall:**
   - Open Windows Defender Firewall
   - Click "Advanced settings"
   - Create new Inbound Rule for port 5000
   - Allow the connection for Private and Domain networks

2. **Find your IP:**
   ```cmd
   ipconfig
   ```
   Look for "IPv4 Address" under your active network adapter

### Linux

1. **Configure Firewall (if using UFW):**
   ```bash
   sudo ufw allow 5000/tcp
   sudo ufw reload
   ```

2. **Find your IP:**
   ```bash
   hostname -I
   # or
   ip addr show
   ```

### Docker Desktop on Windows/Mac

Docker Desktop binds to 0.0.0.0 by default, making the service accessible from the LAN. Ensure your firewall allows incoming connections on port 5000.

## 📁 Project Structure

```
BasicWebServer/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── app.py               # Main Flask application
│   ├── models.py            # Database models
│   └── templates/
│       └── index.html       # Frontend template
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Test configuration
│   └── test_app.py          # Application tests
├── Dockerfile               # Docker container definition
├── docker-compose.yml       # Multi-container Docker setup
├── init-db.sql             # Database initialization
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🔒 Security Considerations

This is a basic forum for LAN use and traffic recording. For production use, consider:

- ✅ Change default database credentials
- ✅ Use strong SECRET_KEY for Flask sessions
- ✅ Implement rate limiting
- ✅ Add input sanitization for XSS prevention
- ✅ Use HTTPS with proper certificates
- ✅ Implement CSRF protection
- ✅ Add content moderation
- ✅ Set up proper logging and monitoring

## 🐛 Troubleshooting

### Cannot connect from other devices on LAN

1. Verify the server is running: `docker-compose ps`
2. Check firewall settings on the host machine
3. Ensure devices are on the same network
4. Verify the host IP address is correct
5. Try accessing http://[HOST_IP]:5000 from the host first

### Database connection errors

1. Check PostgreSQL is running: `docker-compose ps`
2. Verify database credentials in `.env` or `docker-compose.yml`
3. Check database logs: `docker-compose logs db`
4. Ensure the database container is healthy: `docker-compose ps`

### Port already in use

Change the port in `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Use port 8080 instead of 5000
```

### Application not updating

1. Rebuild containers: `docker-compose up -d --build`
2. Clear browser cache
3. Check application logs: `docker-compose logs web`

## 📊 Monitoring and Logs

### View Application Logs
```bash
docker-compose logs -f web
```

### View Database Logs
```bash
docker-compose logs -f db
```

### View All Logs
```bash
docker-compose logs -f
```

### Check Container Status
```bash
docker-compose ps
```

## 🤝 Contributing

This is a basic educational project. Feel free to fork and modify for your needs.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎯 Purpose

This web server is designed for recording user traffic patterns for classification purposes. The anonymous forum provides a functional interface that generates realistic user interactions with a web server, making it suitable for:

- Network traffic analysis
- User behavior pattern studies
- Web server performance testing
- Educational demonstrations
- LAN-based communication experiments

## 📞 Support

For issues and questions:
1. Check the Troubleshooting section
2. Review application logs
3. Verify your Docker and network configuration
4. Create an issue on GitHub with:
   - Description of the problem
   - Steps to reproduce
   - Environment details (OS, Docker version, etc.)
   - Relevant log outputs