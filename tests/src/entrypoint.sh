#!/bin/sh

set -e

echo "TLS_CACERT  /ssl/ca.crt" > /etc/openldap/ldap.conf

exec pytest -s -vvv tests/ $@
