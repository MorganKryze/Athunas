FROM python:3.11-slim-bookworm

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        git \
        libsixel-dev \
        python3-tk \
        cython3 \
        libcap2-bin \
        python3-dev \
        python3-pil \
        python3-setuptools && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy all application code
COPY . .

# Initialize and update git submodules
RUN git submodule update --init --recursive || true

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Build rpi-rgb-led-matrix library (examples and Python bindings)
RUN make -C ./rpi-rgb-led-matrix/examples-api-use && \
    make -C ./rpi-rgb-led-matrix build-python && \
    make -C ./rpi-rgb-led-matrix install-python

# Set capabilities for real-time priority
RUN setcap 'cap_sys_nice=eip' /usr/local/bin/python3.11

# Expose Flask port (can be removed if not using Flask)
EXPOSE 5000

# Default command to run the project
CMD ["python", "src"]