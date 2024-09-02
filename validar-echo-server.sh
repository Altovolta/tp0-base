#!/bin/bash

docker build . -f server_test/Dockerfile -t echo_server_test:latest

answer=$(docker run --rm --name=echo-test --env-file=server_test/server_config.txt \
         --network=tp0_testing_net echo_server_test:latest)

if [ "$answer" = "hola" ] 
then 
    echo "action: test_echo_server | result: success"
else 
    echo "action: test_echo_server | result: fail"
fi 

