FROM python:alpine

RUN apk add --no-cache --virtual dev gcc linux-headers musl-dev \
    && pip install --no-binary :all: psutil \
    && apk del dev

WORKDIR /app

ADD main.py .

CMD ./main.py
