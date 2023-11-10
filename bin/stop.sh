#!/bin/bash

docker stop $(docker ps -q --filter ancestor=chat-o-sophy)
docker rm $(docker ps -aq --filter ancestor=chat-o-sophy)
