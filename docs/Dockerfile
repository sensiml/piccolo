FROM sensiml/base:latest
RUN apt-get -yq install pandoc
COPY ./requirements.txt .
RUN pip install -r requirements.txt