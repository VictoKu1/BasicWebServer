FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY tests/ ./tests/

# Create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check (no external deps)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["python","-c","import urllib.request, sys;\\ntry:\\n    r=urllib.request.urlopen('http://localhost:5000/health', timeout=2)\\n    sys.exit(0 if getattr(r,'status',200)==200 else 1)\\nexcept Exception:\\n    sys.exit(1)"]

# Run the application with Gunicorn (stdout logging)
CMD ["gunicorn", "-w", "2", "-k", "gthread", "--threads", "4", "--timeout", "30", "--graceful-timeout", "30", "--access-logfile", "-", "--error-logfile", "-", "-b", "0.0.0.0:5000", "app.app:create_app()"]
