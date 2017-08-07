FROM alpine

RUN  apk update \
  && apk add openssl \
  && rm -rf /var/cache/apk/*

RUN mkdir -p /certificate-authority/private \
    && mkdir -p /certificate-authority/certs \
    && mkdir -p /certificate-authority/newcerts \
    && mkdir -p /certificate-authority/crl \
    && mkdir -p /certificate-authority/csr \
    && touch /certificate-authority/index.txt \
    && echo "01" > /certificate-authority/serial

WORKDIR /certificate-authority

COPY . /certificate-authority/

RUN chmod 700 /certificate-authority/entrypoint.sh

ENTRYPOINT ["/certificate-authority/entrypoint.sh"]
