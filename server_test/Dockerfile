FROM ubuntu:latest
RUN apt-get update && apt install netcat-traditional
CMD echo 'hola' | nc -w 10 $SERVER_IP $SERVER_PORT