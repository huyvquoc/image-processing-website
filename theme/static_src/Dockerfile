FROM node:14

RUN apt-get update --fix-missing
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

RUN curl -sL https://deb.nodesource.com/setup_14.x | bash - \
  && apt-get install -y nodejs --no-install-recommends

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY package*.json ./
# RUN npm install -g nodemon mocha supervisor npm-run-all
RUN npm install

EXPOSE 3000

ENV NODE_ENV=development
ENV DEBUG=true

COPY . .

# CMD [ "npm", "run", "start" ]
# CMD ["npm", "start"]
# CMD ["nodemon", "bin/www"]