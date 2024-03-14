FROM node:17.6.0 AS build-stage
WORKDIR /star-burger/
COPY package*.json .
RUN npm ci --dev
COPY bundles-src ./bundles-src
RUN ./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles

FROM alpine:latest
WORKDIR /star-burger/
RUN mkdir -p /var/www/frontend/
COPY --from=build-stage /star-burger/bundles/* /star-burger/bundles/
CMD ["cp", "-r", "/star-burger/bundles/.", "/var/www/frontend/"]
