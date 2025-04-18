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
COPY run.py .
COPY sum_agent.py .
#COPY schema.sql .
COPY requirements.txt .
COPY .env .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables for Selenium (headless Chrome)
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Command to run the pipeline
CMD ["bash", "-c", "python run.py && python sum_agent.py"]