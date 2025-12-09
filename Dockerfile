# Docker setup for CyberPatriot Runbook

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set environment
ENV DATABASE_URL=mysql+pymysql://root:password@mysql:3306/cyberpatriot_runbook
ENV PYTHONUNBUFFERED=1

# Run application
CMD ["python", "main.py"]
