FROM python:3.9-slim

# Create a non-root user
RUN useradd -m appuser

# Install ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app/ /app

# Change ownership of /app directory
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Expose port 5000
EXPOSE 5000

# Run the application with Gunicorn using gevent worker class and increased timeout
CMD ["gunicorn", "--worker-class", "gevent", "--bind", "0.0.0.0:5000", "--timeout", "28800", "app:app"]

