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
  && apt-get install -y build-essential curl \
  && curl -sL https://deb.nodesource.com/setup_14.x | bash - \
  && apt-get install -y nodejs --no-install-recommends \
  # && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
  && apt-get clean


# RUN apt-get install build-dep python-psycopg2
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 -y
RUN python -m pip install --upgrade pip

WORKDIR /code

# RUN useradd --create-home python \
#   && chown python:python -R /code

# USER python 

# COPY --chown=python:python requirements*.txt ./

COPY requirements_local.txt /code/
RUN pip install -r requirements_local.txt

# ENV DEBUG="${DEBUG}" \
#     PYTHONUNBUFFERED="true" \
#     PATH="${PATH}:/home/python/.local/bin" \
#     USER="python"

# COPY --chown=python:python . /code/
COPY . /code/

WORKDIR /code/theme/static_src
# RUN npm cache clean --force
# RUN rm -rf node_modules
RUN npm install -g nodemon --save-dev
RUN npm install -g npm-run-all browser-sync cross-env
RUN npm install
# RUN npm start
# CMD ["npm", "start"]

WORKDIR /code
ENV DJANGO_SETTINGS_MODULE=signup.settings_docker
RUN SECRET_KEY=nothing python manage.py tailwind install --no-input;
RUN SECRET_KEY=nothing python manage.py tailwind build --no-input;
# RUN SECRET_KEY=nothing python manage.py collectstatic --no-input;

# COPY docker-entrypoint.sh /code/
# RUN chmod +x docker-entrypoint.sh
# ENTRYPOINT ["./docker-entrypoint.sh"]
# USER root
COPY ./docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]