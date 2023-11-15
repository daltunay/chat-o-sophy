#!/bin/bash

export DOCKER_CLI_HINTS=false

if [ "$(docker ps -q --filter ancestor=chat-o-sophy)" ]; then
    docker stop $(docker ps -q --filter ancestor=chat-o-sophy)
    docker rm $(docker ps -q --filter ancestor=chat-o-sophy)
fi

docker build -t chat-o-sophy . &&
docker run -p 8501:8501 chat-o-sophy
