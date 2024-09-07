FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx libgl1-mesa-dri libglib2.0-0

# Set up the virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . /app

# Set the working directory
WORKDIR /app

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
