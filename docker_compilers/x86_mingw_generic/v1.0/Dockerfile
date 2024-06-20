FROM sensiml/base_image:v3.0
LABEL Description="Base Image for setting up SensiML docker runners"

RUN export DEBIAN_FRONTEND=noninteractive && apt-get update -qq -y && apt-get install -y --no-install-recommends \
  mingw-w64 mingw-w64-tools mingw-w64-common mingw-w64-x86-64-dev \
  > /dev/null \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
