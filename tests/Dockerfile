FROM python:3.12-alpine
LABEL maintainer Pierre Verkest <pverkest@anybox.fr>

RUN apk add --update \
  openldap-clients \
  dumb-init \
  && rm -rf /var/cache/apk/* \
  && mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY src/ /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

RUN chmod 700 /usr/src/app/entrypoint.sh

ENTRYPOINT ["dumb-init", "--"]
CMD ["/usr/src/app/entrypoint.sh"]
