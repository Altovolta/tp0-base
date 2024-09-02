#!/bin/bash

docker build . -f server_test/Dockerfile -t echo_server_test:latest

docker network create testing_net

answer=$(docker run --name=echo-test --env-file=server_test/server_config.txt \
         --network=testing_net echo_server_test:latest)

if [ "$answer" == "hola" ] 
then 
    echo "action: test_echo_server | result: success"
else 
    echo "action: test_echo_server | result: fail"
fi 

docker stop echo-test  >/dev/null && docker rm echo-test  >/dev/null 
docker rmi echo_server_test:latest > /dev/null

