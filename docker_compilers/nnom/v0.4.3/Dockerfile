FROM tensorflow/tensorflow:2.14.0rc1
LABEL Description="Image for generating NNOM from model file"


RUN apt-get update -qq && apt-get install -y git jq dos2unix zip unzip vim git \
awscli  > /dev/null \
&& mkdir /build \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/cknorow-sensiml/nnom/ && cd nnom && pip install . && pip install pandas
WORKDIR /
ADD run_build.sh /

RUN chmod +x /run_build.sh
