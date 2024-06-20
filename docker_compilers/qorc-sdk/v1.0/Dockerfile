FROM sensiml/arm_gcc_none_eabi_base:10.3.1-v1.0
LABEL Description="Image for building library/applications for Qorc-SDK"

RUN git clone --depth 1 --recursive https://github.com/QuickLogic-Corp/qorc-sdk.git /build/qorc-sdk && \
  cd /build/qorc-sdk && \
  rm -rf  /build/qorc-sdk/Tools /build/qorc-sdk/docs && \
  find /build/qorc-sdk -type d -name "knowledgepack" -print0 | xargs -0 rm -R

WORKDIR /
