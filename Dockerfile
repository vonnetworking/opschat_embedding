FROM nvidia/cuda:11.8.0-base-ubuntu20.04

# Install dependencies
RUN apt-get update && \
    apt-get install -y python3-pip

# Copy your application code
COPY ./src /app
COPY ./models /app/models

# Set working directory
WORKDIR /app

# Install Python dependencies
RUN pip install -r requirements.txt

# Run your application
CMD ["python3", "app.py"]
