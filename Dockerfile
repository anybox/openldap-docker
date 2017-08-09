FROM alpine
LABEL maintainer Pierre Verkest <pierreverkest84@gmail.com>

ENV OPENLDAP_VERSION 2.4.44-r5

# TODO: make sure those dependencies (openssl gnutls nss cyrus-sasl krb5) are
# runtime requirement, I'm (Pierre V.) not sure if the documentation
# http://www.openldap.org/doc/admin24/install.html
# mentioned those dependencies to build OpenLdap or as extra dependency for
# some use case scenario like using tls / kerberos and so on.

# NOTE: You can add openldap-clients for testing purpose
# NOTE: following package are require for building onpenldap:
# openssl gnutls nss cyrus-sasl krb5
RUN  adduser -D -H -u 666  ldap \
  && apk add --update \
             openldap=$OPENLDAP_VERSION \
             dumb-init \
  && rm -rf /var/cache/apk/* \
  && rm /etc/openldap/*.default \
  && rm /etc/openldap/*.example \
  && rm /etc/openldap/*.ldif \
  && rm /etc/openldap/*.conf \
  && rm -r /var/lib/openldap/openldap-data/*

COPY etc/* /etc/openldap/
COPY entrypoint.sh /entrypoint.sh

VOLUME ["/etc/openldap/slapd.d", "/var/lib/openldap/"]

RUN  chmod 500 /etc/openldap/*.ldif.template.sh \
  && chmod 700 /entrypoint.sh \
  && chown ldap:ldap -R /var/lib/openldap/run/

EXPOSE 389 636

ENTRYPOINT ["dumb-init", "--"]
CMD ["/entrypoint.sh"]
