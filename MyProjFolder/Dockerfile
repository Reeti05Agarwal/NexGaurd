# -----------------------------
# Base Image
# -----------------------------
FROM python:3.11-slim

# -----------------------------
# Set Working Directory
# -----------------------------
WORKDIR /app

# -----------------------------
# Install system dependencies
# -----------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Copy only requirements first for caching
# -----------------------------
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# -----------------------------
# Copy project files
# -----------------------------
COPY . .

# -----------------------------
# Expose port (for FastAPI)
# -----------------------------
EXPOSE 8000

# -----------------------------
# Run FastAPI app
# -----------------------------
CMD ["uvicorn", "MyProjFolder.Inference.fraud_inference:app", "--host", "0.0.0.0", "--port", "8000"]
