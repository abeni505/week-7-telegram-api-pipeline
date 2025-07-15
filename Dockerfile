# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the file with all your dependencies into the container
COPY requirements.txt .

# Install the dependencies from the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application's code into the container
COPY . .

# Specify the command to run when the container starts
CMD ["python", "src/main.py"]
