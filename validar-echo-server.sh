#!/bin/bash

docker build . -f server_test/Dockerfile -t echo_server_test:latest

docker network create -d bridge testing_net
docker network connect testing_net server

answer=$(docker run --rm --name=echo-test --env-file=server_test/server_config.txt \
         --network=testing_net echo_server_test:latest)

if [ "$answer" = "hola" ] 
then 
    echo "action: test_echo_server | result: success"
else 
    echo "action: test_echo_server | result: fail"
fi 

docker container stop server  >/dev/null && docker rm server  >/dev/null 
docker rmi echo_server_test:latest > /dev/null
docker network rm -f testing_net >/dev/null

