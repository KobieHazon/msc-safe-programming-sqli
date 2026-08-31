#!/bin/bash
if [ ! -d "./ex1" ] 
then
    mkdir ex1
    tar -C ex1 -xvzf ex1-prod.tar.gz
    cd ex1
    docker load -i web_server.tar.gz
    docker load -i sql_server.tar.gz
else
    cd ex1
fi
docker-compose up
