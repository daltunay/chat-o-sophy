#!/bin/bash

CONTAINER_IDS=$(docker ps -q --filter ancestor="chat-o-sophy")

if [ -n "$CONTAINER_IDS" ]; then
    docker stop $CONTAINER_IDS
    docker rm $CONTAINER_IDS
fi

PROCESS_IDS=$(lsof -ti tcp:8501)

if [ -n "$PROCESS_IDS" ]; then
    kill -9 $PROCESS_IDS
fi
