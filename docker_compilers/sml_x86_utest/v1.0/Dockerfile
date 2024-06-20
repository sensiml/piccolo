FROM sensiml/base_image:v3.0
LABEL Description="Image for building x86 library gtest"

RUN apt-get update -qq && \
    apt-get install -y \
    libgtest-dev \
    cmake && \
    apt-get clean && \
    cd /usr/src/googletest && \
    cmake . && \
    cmake --build . --target install