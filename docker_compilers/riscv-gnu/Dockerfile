FROM sensiml:base_image:v3.0
LABEL Author="Chris Knorowski <chris.knorowski@senisml.com>"
LABEL Description="Image for running riscv-gnu crosscompiler for newlib"
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections
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
  autoconf \ 
  automake \
  autotools-dev \
  curl \
  python3 \
  python3-pip \
  libmpc-dev \
  libmpfr-dev \
  libgmp-dev \
  gawk \
  bison \
  flex \
  texinfo \
  gperf \
  libtool \
  patchutils \
  bc \
  zlib1g-dev \
  libexpat-dev \
  ninja-build \
  git \
  cmake \
  libglib2.0-dev \
  libslirp-dev \
  zip > /dev/null \
  && mkdir /build \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
RUN git clone https://github.com/riscv/riscv-gnu-toolchain && \
        cd riscv-gnu-toolchain && \
        ./configure --prefix=/opt/riscv && \
        make