# Use an appropriate base image
FROM python:3.10-slim

# Install OpenGL dependencies
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Set up the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH"

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
