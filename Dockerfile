FROM python:3.8
ENV PYTHONUNBUFFERED=1
# RUN apt-get -yqq update
# RUN apt-get -yqq install python3-pip python3-dev curl gnupg
RUN apt-get update && apt-get install

RUN apt-get install -y \
  dos2unix \
  libpq-dev \
  libmariadb-dev-compat \
  libmariadb-dev \
  gcc \
  && apt-get clean

# RUN apt-get install build-dep python-psycopg2
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 -y
RUN python -m pip install --upgrade pip

WORKDIR /code
COPY requirements_local.txt /code/
RUN pip install -r requirements_local.txt
COPY . /code/