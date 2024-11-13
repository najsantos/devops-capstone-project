# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json files
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application contents
COPY service/ ./service/

# Create and switch to a non-root user
RUN useradd --uid 1000 theia && chown -R theia /app
USER theia

# Expose the port on which the application will run
EXPOSE 8080

# Specify the default command to run the service
CMD ["gunicorn", "--bind=0.0.0.0:8080", "--log-level=info", "service:app"]
