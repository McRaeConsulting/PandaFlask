###########
# BUILDER #
###########

# pull official base image
FROM python:3.8 as builder

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive

# install system dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends gcc

# lint
RUN pip install --upgrade pip
RUN pip install flake8
COPY . /usr/src/app/
RUN flake8 --ignore=E501,F401 covid_data

# install web dependencies
COPY ./covid_data/requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


#########
# FINAL #
#########

# pull official base image
FROM python:3.8

# create directory for the app user
RUN mkdir -p /home/app

RUN mkdir /data

# create the app user
RUN addgroup app && adduser --quiet --no-create-home --ingroup app --disabled-password --disabled-login  --gecos "" app

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
ENV DEBIAN_FRONTEND=noninteractive

RUN mkdir -p "$APP_HOME"
WORKDIR "$APP_HOME"

# install dependencies
RUN apt-get update && \
    apt-get upgrade -y

COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

# copy project
COPY . "$APP_HOME"

COPY publishedweek392020.xlsx /data/
# chown all the files to the app user
RUN chown -R app:app "$APP_HOME"

# change to the app user
USER app

