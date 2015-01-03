FROM ubuntu:14.04

RUN  apt-get update && apt-get install -y software-properties-common python python-dev python-pip libffi-dev libpq-dev git-core postgresql-client \
    && apt-get clean \
    && apt-get autoclean \
    && sudo apt-get autoremove -y \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/

RUN mkdir /opt/code
ADD . /opt/code
WORKDIR /opt/code

RUN python setup.py develop

VOLUME ["/opt/code"]

CMD ["python", "setup.py", "test"]
