# Use a base image with Python installed
FROM python:3.9-slim

# Install system dependencies needed for PyQt5 and OpenGL
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    libxrender-dev \
    libxext-dev \
    libx11-dev \
    libgl1-mesa-glx \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . /app/

# Set the command to run the application
CMD ["python", "mode_based.py"]
