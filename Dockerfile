FROM python:3.7-alpine

WORKDIR /pinger
COPY pinger .
COPY requirements.txt requirements.txt
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install -r requirements.txt

ENV PING_HOSTS google.com
ENV FLASK_ENV development
ENV PING_DELAY_SEC 30
ENV DB_URL postgresql://postgres:postgres@db/pinger
