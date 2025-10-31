FROM python:3.11-slim-bookworm

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        git \
        libsixel-dev \
        python3-tk \
        cython3 \
        libcap2-bin && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Set capabilities for real-time priority
RUN setcap 'cap_sys_nice=eip' /usr/local/bin/python3.11

# Expose Flask port
EXPOSE 5000