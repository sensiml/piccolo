FROM ghcr.io/tflm-bot/tflm-ci:latest


ENV GECKO_SDK_PATH=/gecko_sdk
ENV CMSIS_PATH=/tflite-micro/tensorflow/lite/micro/tools/make/downloads/cmsis/

# checkout tensorflow source
WORKDIR /

RUN pip install --upgrade pip

RUN apt-get update -qq -y && apt-get install -y --no-install-recommends \
  vim \
  jq \
  unzip \
  zip > /dev/null \
  && rm -rf /var/lib/apt/lists/* \
  && pip install awscli \
  && pip install absl-py \
  && apt-get clean


RUN git clone https://github.com/sensiml/tflite-micro.git --depth 1 --branch sensiml-rebase && \
  git clone https://github.com/sensiml/gecko_sdk --depth 1 --branch gsdk_4.3

ADD run_build.sh /
RUN pip install tflite-micro

RUN  cd /tflite-micro && git pull \
  && cd /tflite-micro/tensorflow/lite/micro/examples/model_runner/codegen &&  python codegen.py --model_json_path=test_model.json \
  && cd /tflite-micro/ \
  && make -f tensorflow/lite/micro/tools/make/Makefile TENSORFLOW_ROOT=/tflite-micro/ generate_model_runner_make_project TARGET=cortex_m_generic TARGET_ARCH=cortex-m4+fp OPTIMIZED_KERNEL_DIR=cmsis_nn SKIP_PIGWEED_DOWNLOAD=true SKIP_COMPILER_DOWNLOAD=true \
  && make -j -f tensorflow/lite/micro/tools/make/Makefile TARGET=mplab_xc32 TARGET_ARCH=ATSAMD21G18A generate_model_runner_make_project TOOLCHAIN=xc32- SKIP_PIGWEED_DOWNLOAD=true SKIP_COMPILER_DOWNLOAD=true \    
  && rm -rf /tflite-micro/gen \
  && bazel run tensorflow/lite/micro/tools/gen_micro_mutable_op_resolver:generate_micro_mutable_op_resolver_from_model -- --common_tflite_path=/tflite-micro/tensorflow/lite/micro/examples/model_runner/codegen/ --input_tflite_files=model.tflite --output_dir=/tflite-micro/tensorflow/lite/micro/ \
  && bazel run tensorflow/lite/tools:strip_strings  -- --input_tflite_file=/tflite-micro/tensorflow/lite/micro/examples/model_runner/codegen/model.tflite --output_tflite_file=./model.stripped.tflite