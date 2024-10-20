# Use an official Python runtime as a base image (slim version for smaller size)
FROM python:3.9-slim

# Set environment variables for non-interactive apt installs and to optimize for production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a non-root user and set a working directory
RUN useradd -m appuser
WORKDIR /usr/src/app

# Copy the requirements.txt file first to leverage Docker caching
COPY requirements.txt .

# Install any needed packages from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Change ownership of the directory to the non-root user
RUN chown -R appuser /usr/src/app

# Switch to the non-root user
USER appuser

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run FastAPI with uvicorn, binding to 0.0.0.0 and port 8000
CMD ["fastapi", "run", "app.py","--host", "0.0.0.0", "--port", "8000"]
