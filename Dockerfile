# Use a slim Python base
FROM python:3.11-slim

# Install system dependencies for wkhtmltopdf
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wkhtmltopdf \
    build-essential \
    libssl-dev \
    libffi-dev \
    libjpeg-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for Flask
EXPOSE 5000

# Run the Flask app
CMD ["python", "main.py"]
