# BasicWebServer: Anonymous Forum

A simple, single threaded anonymous forum web application built with Flask and PostgreSQL. This application allows users on the same LAN to connect, read comments, and post their own thoughts without requiring login or sign up.

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

## 🧰 Required Software

- **Docker Engine / Docker Desktop**: 20.10+
  - Windows/macOS: Docker Desktop
  - Linux: Docker Engine (plus Compose plugin)
  - Download: [Docker Desktop](https://www.docker.com/products/docker-desktop) • [Docker Engine](https://docs.docker.com/engine/install/)
  - Verify: `docker --version`

- **Docker Compose v2**: Included with Docker Desktop, or `docker compose` plugin on Linux
  - Docs: [Compose V2](https://docs.docker.com/compose/)
  - Verify: `docker compose version` (or `docker-compose --version`)

- **Git**: For cloning the repository
  - Download: [git-scm.com](https://git-scm.com/downloads)
  - Verify: `git --version`

- **Python 3.11+**: For local development and running tests outside Docker
  - Download: [python.org](https://www.python.org/downloads/)
  - Verify: `python --version` and `pip --version`

- **PostgreSQL 15+**: Only required for local development without Docker
  - Download: [postgresql.org](https://www.postgresql.org/download/)
  - Verify: `psql --version`

- Optional tools
  - **PowerShell 7+** or **Bash**: convenient shell environment
  - **curl**: for quick HTTP checks (`curl --version`)

### Windows
- Install Docker Desktop and enable WSL 2 backend if prompted.
- Install Python from `python.org` or Microsoft Store (ensure “Add to PATH”).
- Install Git for Windows.
- PostgreSQL: use the official Windows installer.

### Quick verification (Windows PowerShell)
```powershell
docker --version
docker compose version
git --version
python --version
pip --version
psql --version
```

### Linux
- Install Docker Engine and Compose Plugin (distro-specific):
  - Ubuntu/Debian (example):
    ```bash
    sudo apt update
    sudo apt install -y docker.io docker-compose-plugin
    sudo systemctl enable --now docker
    sudo usermod -aG docker $USER  # re-login required
    ```
  - Note: You must log out and back in (or reboot) for group changes to take effect. Until then, use `sudo` with Docker commands (e.g., `sudo docker compose version`).
- Install Python 3.11+ and pip via your package manager.
- Install Git via your package manager.
- PostgreSQL: install via your package manager (or use Docker instead).

### Quick verification (Linux / Bash)
```bash
docker --version
docker compose version || docker-compose --version
git --version
python3 --version
pip3 --version
psql --version
```

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

> Note (Linux): If your user is not in the `docker` group or you haven’t re-logged after adding it, prefix Docker commands with `sudo`, for example:
> - `sudo docker compose up -d` (Compose v2)
> - `sudo docker-compose up -d` (legacy Compose)

This will:
- Build the Flask application container
- Pull and start PostgreSQL database container
- Initialize the database with the required schema
- Start Redis (rate limiting storage) and the web server on port 5000

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

# Rate Limiting (optional; defaults to in-memory if not set)
# Use Redis in docker-compose by default:
RATELIMIT_STORAGE_URL=redis://redis:6379/0
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
# Build the image (includes the tests/ directory)
docker-compose build

# Run tests in a temporary container
docker-compose run --rm web python -m pytest -v

# Recommended: allow a writable cache dir only for tests (uses web_test service)
docker-compose run --rm web_test python -m pytest -v

# If you see pytest cache warnings due to read-only FS, disable cache:
docker-compose run --rm web python -m pytest -v -p no:cacheprovider
```

Note: The test suite uses an in-memory SQLite database and does not require the PostgreSQL container to be running

### Running Tests Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run tests:
```bash
pytest -v
```

3. Run tests with coverage:
```bash
# First install plugin if you don't have it:
pip install pytest-cov

pytest -v --cov=app --cov-report=html
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

## 🔒 Security Considerations

This is a basic forum for LAN use and traffic recording. For production use, consider:

- ✅ Change default database credentials
- ✅ Use strong SECRET_KEY for Flask sessions
- ✅ Rate limiting enabled (Redis-backed in Docker); tune limits as needed
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

### Limiter storage warning (development)

If you see a warning about in-memory storage for rate limiting, ensure Redis is running (Compose brings it up automatically) and that the environment variable is set:

```bash
# docker-compose.yml sets this for web:
RATELIMIT_STORAGE_URL=redis://redis:6379/0
```

If you’re running locally without Docker, either install Redis and set the variable accordingly or accept the in-memory backend for development.

### Pytest: "file or directory not found: tests/"

This occurs when the Docker image was built before tests were added to the image. Rebuild the image so it includes the `tests/` directory:

```bash
docker-compose build
docker-compose run --rm web python -m pytest -v
```

### Pytest cache warnings in read-only container

The `web` container filesystem is hardened as read-only, so pytest may warn about failing to write `.pytest_cache`. This is harmless. Options:

```bash
# Preferred: disable pytest cache for the run
docker-compose run --rm web python -m pytest -v -p no:cacheprovider

# Or mount a writable cache directory
docker-compose run --rm -v /tmp/pytest_cache:/app/.pytest_cache web python -m pytest -v
```

## 📊 Monitoring and Logs

### View Application Logs
```bash
docker-compose logs -f web
```

### View Database Logs
```bash
docker-compose logs -f db
```

### View Redis Logs
```bash
docker-compose logs -f redis
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

This is a basic educational project. Feel free to fork and modify for your needs

## 📝 License

This project is licensed under the MIT License,  see the [LICENSE](LICENSE) file for details.


