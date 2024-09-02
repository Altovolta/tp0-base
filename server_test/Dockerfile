FROM ubuntu:latest
RUN apt-get update && apt install netcat-traditional
CMD echo 'hola' | nc $SERVER_IP $SERVER_PORT