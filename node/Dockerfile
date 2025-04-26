#
# Simple backend demo server image
#

FROM ghcr.io/maxotta/kiv-dsa-vagrant-base-docker:latest

RUN yum -q -y install python3
RUN yum -q -y install python3-pip
RUN pip3 install requests

COPY python /opt/node

CMD /usr/bin/python3 /opt/node/node.py

# EOF
