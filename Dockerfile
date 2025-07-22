# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the file with all your dependencies into the container
COPY requirements.txt .

# Install the dependencies from the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Set up dbt profile 
# Create the default dbt directory
RUN mkdir -p /root/.dbt
# Copy the profiles.yml file into the default dbt directory
COPY profiles.yml /root/.dbt/profiles.yml


# Copy your application's code into the container
COPY . .

# Specify the command to run when the container starts
CMD ["python", "src/main.py"]
