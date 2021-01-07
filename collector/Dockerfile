FROM python:alpine

RUN pip install influxdb #retrying

WORKDIR /app

ADD main.py .

CMD ./main.py
