FROM debian:stable


# Get prerequisites for updateGatewayMetrics.py.
RUN apt update
RUN apt install python3 python3-pip -y
RUN pip3 install requests 
RUN apt remove python3-pip -y; apt autoremove -y

# Make a new user with read-only access, and copy updateGatewayMetrics.py to the user's home.
RUN useradd metrics_observer
WORKDIR /home/metrics_observer
COPY updateGatewayMetrics.py .
RUN chown -R metrics_observer:metrics_observer /home/metrics_observer

# No entry point is necessary here, as that will be overridden by docker-compose.yml.