FROM node:latest

ADD ./src /src
WORKDIR /src
EXPOSE 8080

RUN npm install

CMD ["yarn", "serve"]