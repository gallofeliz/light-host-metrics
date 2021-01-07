FROM python:alpine

RUN apk add --no-cache py3-psutil

WORKDIR /app
RUN cp -R /usr/lib/python3.8/site-packages/psutil /app/psutil

ADD main.py .

CMD ./main.py
