FROM sensiml/arm_gcc_none_eabi_base:10.3.1-v1.0

ADD sensiml_recognition_motion.tar.gz /build
ADD sensiml_recognition_audio.tar.gz /build

ENV GECKO_SDK_PATH=/gecko_sdk

RUN find /build -type d -name "knowledgepack" -print0 | xargs -0 rm -R && \
    git clone https://github.com/sensiml/gecko_sdk --depth 1 --branch gsdk_4.3 && \
    cd gecko_sdk && find . -type f -size +1M | xargs rm 


