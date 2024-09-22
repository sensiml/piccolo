FROM python:3.11
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install --no-install-recommends --yes libusb-1.0-0-dev postgresql-client curl software-properties-common sudo \
    && useradd -m sml-app && adduser sml-app sudo && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
WORKDIR /home/sml-app/
COPY ./src/server/requirements.txt .
RUN pip install -r requirements.txt \
    && python -c "from mltk.core.tflite_micro.accelerators.mvp.estimator.utils import download_estimators; download_estimators()"
