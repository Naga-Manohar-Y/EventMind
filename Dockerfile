# Use Python 3.11 slim base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Selenium, Chrome, and Python packages
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip to latest version
RUN pip install --no-cache-dir --upgrade pip

# Copy project files
COPY src/ src/
COPY tests/ tests/
COPY app.py .
COPY run.py .
COPY sum_agent.py .
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables for Selenium (headless Chrome)
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# No CMD; Streamlit will be started via docker-compose.yml