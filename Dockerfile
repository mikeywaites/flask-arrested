FROM python:3.5

RUN mkdir /opt/code
ADD . /opt/code
WORKDIR /opt/code

RUN pip install -U pip
RUN pip install -U setuptools
RUN python setup.py develop

VOLUME ["/opt/code"]

CMD ["python", "setup.py", "test"]
