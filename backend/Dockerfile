FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy legacy modules from root directory
COPY timedomain.py frequencydomain.py filterprocess.py \
     waveletprocess.py hilbertransfer.py harmonic_sildband_table.py \
     x_parameter.py y_parameter.py z_parameter.py \
     initialization.py ./

# Copy backend application code
COPY backend/ .

# Expose port
EXPOSE 8081

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]
