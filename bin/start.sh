#!/bin/bash

export DOCKER_CLI_HINTS=false

docker build -t chat-o-sophy .
docker run -p 8501:8501 chat-o-sophy

echo "The app is now running locally. You can access it in your web browser at: http://localhost:8501"
