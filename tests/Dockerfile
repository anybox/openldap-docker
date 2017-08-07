FROM python:3-alpine3.6
LABEL maintainer Pierre Verkest <pverkest@anybox.fr>

RUN  apk update \
  && apk add openldap-clients \
  && rm -rf /var/cache/apk/* \
  && mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY . /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

RUN chmod 700 /usr/src/app/entrypoint.sh

CMD ["/usr/src/app/entrypoint.sh"]