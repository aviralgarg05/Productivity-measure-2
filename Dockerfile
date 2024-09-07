# Install OpenGL dependencies
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Set up the virtual environment and install Python dependencies
RUN python -m venv --copies /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install -r requirements.txt
