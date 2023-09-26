# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Change to the directory containing manage.py
WORKDIR /app/BCCT

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME World

# Run manage.py migrate to apply database migrations
RUN python manage.py server

# Run gunicorn for the app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myproject.wsgi:application"]