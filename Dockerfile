# pull official base image
FROM python:3.8.10
# set work directory
WORKDIR /usr/src/app
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# install dependencies
RUN apt-get update && apt-get install -y postgresql-client gcc python3 musl libboost-all-dev libgtk-3-dev build-essential cmake
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt
# copy project
COPY . .