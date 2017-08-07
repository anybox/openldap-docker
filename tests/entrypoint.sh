#!/bin/sh

set -e

echo "TLS_CACERT  /ssl/ca.crt" > /etc/openldap/ldap.conf

nosetests -s -v $@
