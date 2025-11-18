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
    CMD python - <<'PY' || exit 1 \
import urllib.request \
try: \
    with urllib.request.urlopen('http://localhost:5000/health', timeout=2) as r: \
        exit(0 if r.status == 200 else 1) \
except Exception: \
    exit(1) \
PY

# Run the application
CMD ["python", "-m", "app.app"]
