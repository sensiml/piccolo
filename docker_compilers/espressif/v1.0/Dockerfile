FROM sensiml/base_image:v3.0
LABEL Description="Image for building ESP32 library for Espressif"

# Download espressif requirements 
RUN apt-get update -qq && apt-get install -y \
    git \
    wget \
    flex \
    bison \
    gperf \
    python3 \
    python3-venv \
    cmake \
    ninja-build \
    ccache \
    libffi-dev \
    libssl-dev \
    dfu-util \
    libusb-1.0-0 \
    > /dev/null \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Download espressif compiler and set it up to be used.
RUN mkdir -p ~/esp && cd ~/esp && \
    git clone --depth 1 --recursive -b v5.0 https://github.com/espressif/esp-idf.git && \
    cd esp-idf && \
    ./install.sh esp32

WORKDIR /
