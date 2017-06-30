FROM python:3

RUN pip install flask && \
    pip install flask-sqlalchemy && \
    pip install py-kim && \
    mkdir -p /opt/code

WORKDIR /opt/code/
ADD . /opt/code
RUN python setup.py develop

EXPOSE 5000
ENV FLASK_APP /opt/code/example/app.py
CMD ["flask", "run", "--port", "5000", "--host", "0.0.0.0"]
