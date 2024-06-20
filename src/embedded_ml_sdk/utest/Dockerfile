FROM ubuntu:latest
LABEL Author="Chris Knorowski <chris.knorowski@sensiml.com>"
LABEL Description="Image for building x86 library gtest"

RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

RUN apt-get update -qq && \
    apt-get install -y \
    build-essential \
    unzip \
    libgtest-dev \
    dos2unix \
    jq \
    cmake \    
    zip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir /build && \
    cd /usr/src/googletest && \
    cmake . && \
    cmake --build . --target install

ADD run_build.sh /