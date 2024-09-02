FROM ubuntu:latest
RUN apt-get update && apt install netcat-traditional
CMD echo 'hola' | nc -v $SERVER_IP $SERVER_PORT