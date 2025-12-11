FROM python:3.11-slim-bookworm

# Install system dependencies (excluding python3-pil to avoid conflicts with pip Pillow)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        git \
        make \
        libsixel-dev \
        python3-tk \
        cython3 \
        libcap2-bin \
        python3-dev \
        python3-setuptools \
        libjpeg-dev \
        zlib1g-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libopenjp2-7-dev \
        libtiff-dev \
        libwebp-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml ./

# Install Python dependencies first (includes Pillow with headers needed for building)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Copy all application code
COPY . .

# Clone rpi-rgb-led-matrix if not present (for CI/CD builds without submodules)
RUN if [ ! -f ./rpi-rgb-led-matrix/Makefile ]; then \
        rm -rf ./rpi-rgb-led-matrix && \
        git clone https://github.com/hzeller/rpi-rgb-led-matrix.git ./rpi-rgb-led-matrix; \
    fi

# Build rpi-rgb-led-matrix library (examples and Python bindings)
# Add Pillow include directory to CFLAGS so gcc can find Imaging.h
RUN export PILLOW_INCLUDE=$(python -c "import PIL; import os; print(os.path.dirname(PIL.__file__))") && \
    export CFLAGS="-I${PILLOW_INCLUDE}" && \
    make -C ./rpi-rgb-led-matrix/examples-api-use && \
    make -C ./rpi-rgb-led-matrix build-python && \
    make -C ./rpi-rgb-led-matrix install-python

# Set capabilities for real-time priority
RUN setcap 'cap_sys_nice=eip' /usr/local/bin/python3.11

# Expose Flask port (can be removed if not using Flask)
EXPOSE 5000

# Default command to run the project
CMD ["python", "src"]