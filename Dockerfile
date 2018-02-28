FROM lsiobase/alpine:3.7

RUN apk add --no-cache python3 sqlite
RUN pip3 install bottle dataset pygments

COPY src/ /src
COPY root/ /

EXPOSE 8080
VOLUME /config
