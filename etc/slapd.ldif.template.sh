#!/bin/sh

set -e

USAGE="Usage: $0 -C Certificate path -K Certificate key file
                 [-A CA path] [-V TLS Verify client]
                 [-S CIPHER suite] [-h]

Template to generate slapd ldif config file

Options:
    -C Certificate          Certificate file
    -K Certificate key      Certificate key file
    -A CA path              Certificate authority in case of self signed
                            certificate (default: None)
    -V TLS Verify Client    (default: never)
    -S CIPHER suite         (default: DEFAULT)
    -h
"


while getopts "C:K:A:V:h" OPTION
do
    case $OPTION in
        C) CERTIF_PATH=$OPTARG;;
        K) CERTIF_KEY_PATH=$OPTARG;;
        A) CA_PATH=$OPTARG;;
        V) TLS_VERIF_CLIENT=$OPTARG;;
        S) CIPHER=$OPTARG;;
        h) echo "$USAGE";
           exit;;
        *) echo "Unknown parameter while generating slapd ldif template" >&2;
           echo "$USAGE" >&2;
           exit 1;;
    esac
done

if [[ ! $CERTIF_PATH ]]; then
    echo "Missing certificat path while generating slapd ldif template" >&2
    exit 1
fi
if [[ ! $CERTIF_KEY_PATH ]]; then
    echo "Missing certificat key path while generating slapd ldif template" >&2
    exit 1
fi

if [[ -f $CA_PATH ]]; then
    CA_PATH="olcTLSCACertificateFile: $CA_PATH"
else
    CA_PATH="# olcTLSCACertificateFile: No CA provided"
fi

TLS_VERIF_CLIENT=${TLS_VERIF_CLIENT:-never}
CIPHER=${CIPHER:-DEFAULT}

cat << EOF
#
# See slapd-config(5) for details on configuration options.
# This file should NOT be world readable.
#
dn: cn=config
objectClass: olcGlobal
cn: config
olcTLSCertificateFile: $CERTIF_PATH
olcTLSCertificateKeyFile: $CERTIF_KEY_PATH
olcTLSVerifyClient: $TLS_VERIF_CLIENT
olcTLSCipherSuite: $CIPHER
$CA_PATH
#
# Define global ACLs to disable default read access.
#
olcArgsFile: /var/lib/openldap/run/slapd.args
olcPidFile: /var/lib/openldap/run/slapd.pid
#
# Do not enable referrals until AFTER you have a working directory
# service AND an understanding of referrals.
#olcReferral:   ldap://root.openldap.org
#
# Sample security restrictions
# Sample security restrictions
#   Require integrity protection (prevent hijacking)
#   Require 112-bit (3DES or better) encryption for updates
#   Require 64-bit encryption for simple bind
#olcSecurity: ssf=1 update_ssf=112 simple_bind=64

dn: cn=module,cn=config
objectClass: olcModuleList
objectClass: top
cn: module
olcModulepath: /usr/lib/openldap
olcModuleload: memberof
olcModuleload: refint
olcModuleload: ppolicy

dn: cn=schema,cn=config
objectClass: olcSchemaConfig
cn: schema

include: file:///etc/openldap/schema/core.ldif
include: file:///etc/openldap/schema/cosine.ldif
include: file:///etc/openldap/schema/inetorgperson.ldif
include: file:///etc/openldap/schema/ppolicy.ldif

# Frontend settings
#
dn: olcDatabase=frontend,cn=config
objectClass: olcDatabaseConfig
objectClass: olcFrontendConfig
olcDatabase: frontend

EOF
