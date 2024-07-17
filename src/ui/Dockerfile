# pull official base image
FROM node:16-alpine3.15
# set working directory
WORKDIR /sml_webui
# add `/sml_webui/node_modules/.bin` to $PATH
ENV PATH /sml_webui/node_modules/.bin:$PATH
# install sml_webui dependencies
RUN apk update && apk add -y --no-cache curl zip jq bash aws-cli
