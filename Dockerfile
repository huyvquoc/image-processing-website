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

# COPY docker-entrypoint.sh /code/
# RUN chmod +x docker-entrypoint.sh
# ENTRYPOINT ["./docker-entrypoint.sh"]
# USER root
COPY ./docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]

# ========================================
FROM python:3.8

WORKDIR /code

RUN apt-get update \
  && apt-get install -y build-essential curl \
  && curl -sL https://deb.nodesource.com/setup_14.x | bash - \
  && apt-get install -y nodejs --no-install-recommends \
  && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
  && apt-get clean \
  && useradd --create-home python \
  && chown python:python -R /code

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 -y
RUN python -m pip install --upgrade pip

USER python

COPY --chown=python:python requirements*.txt ./

RUN pip install -r requirements_local.txt

ENV DEBUG="${DEBUG}" \
    PYTHONUNBUFFERED="true" \
    PATH="${PATH}:/home/python/.local/bin" \
    PATH="${PATH}:/code/theme/static_src/node_modules/.bin" \
    USER="python"

COPY --chown=python:python . .

WORKDIR /code/theme/static_src
# RUN npm install -g nodemon --save-dev
# RUN npm install -g npm-run-all browser-sync cross-env
RUN npm install

WORKDIR /code

ENV DJANGO_SETTINGS_MODULE=signup.settings_docker
RUN SECRET_KEY=nothing python manage.py tailwind install --no-input;
RUN SECRET_KEY=nothing python manage.py tailwind build --no-input;
RUN SECRET_KEY=nothing python manage.py collectstatic --no-input;

CMD ["python", "manage.py", "runserver"]