FROM python:2

ADD ./requirements.txt /opt/code/requirements.txt

RUN pip install -r /opt/code/requirements.txt

WORKDIR /opt/code/

ADD . /opt/code
RUN python setup.py develop
CMD ["py.test"]
