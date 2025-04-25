#
# Setup image with NGINX as frontend (proxy) server
#

FROM ghcr.io/maxotta/kiv-dsa-vagrant-base-docker:latest

RUN yum -q -y install python3
RUN yum -q -y install python3-pip
RUN pip3 install flask

COPY python /opt/monitor

CMD /usr/bin/python3 /opt/monitor/monitor.py
