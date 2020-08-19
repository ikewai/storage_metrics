FROM debian:stable

WORKDIR /usr/src/app

RUN apt update
RUN apt install python3 python3-pip -y
RUN pip3 install requests
RUN apt remove python3-pip -y; apt autoremove -y

COPY updateGatewayMetrics.py .

CMD [ "sleep", "infinity" ]