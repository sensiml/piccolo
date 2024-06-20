FROM ubuntu:latest
LABEL Description="Base Image for setting up SensiML docker runners"

RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

ADD run_build.sh /

RUN chmod +x /run_build.sh
RUN apt-get update -qq && apt-get install -y \
  build-essential \
  wget \
  git \
  git-lfs \
  dos2unix \
  unzip \
  vim \
  jq \
  awscli \
  zip > /dev/null \
  && mkdir /build \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY CMSIS_5 /build/CMSIS_5
COPY CMSIS-DSP /build/CMSIS-DSP
COPY CMSIS-NN /build/CMSIS-NN
