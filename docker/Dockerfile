FROM python:3.8-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get -y update && apt-get install -y \
    libmemcached-dev \
    zlib1g-dev \
    gcc
RUN pip install --upgrade pip

RUN mkdir /app
RUN mkdir /app/requirements
WORKDIR /app

ADD requirements /app/requirements
RUN pip install -r /app/requirements/development.txt