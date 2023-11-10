#!/bin/bash

export DOCKER_CLI_HINTS=false

docker build -t chat-o-sophy .
docker run -p 8501:8501 chat-o-sophy
