# syntax=docker/dockerfile:1

FROM python:3.11-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git && \
    apt-get install gcc

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "bot/main.py" ]
