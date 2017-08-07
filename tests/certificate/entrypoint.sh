#!/bin/sh

set -e
set -x

CA_DOMAIN=${CA_DOMAIN:-ci.example.com}
CERT_SUB_DOMAIN=${CERT_SUB_DOMAIN:-ldap}
OUTPUT_DIR=${OUTPUT_DIR:-/certificate}
GID=${GID:-0}
UID=${UID:-0}

USAGE="Usage: $0 [-D CA DOMAIN] [-S CERT_SUB_DOMAIN] [-o OUTPUT DIR]
                 [-G GROUP ID] [-U UID] [-h]

Script to generate CA and certificate for testing purpose.

> **DISCLAIMER**: Generated file should not be used in production server

Options:
    -D CA_DOMAIN            Certificat Authority Domain.
                            can be set using env var CA_DOMAIN
                            (default: $CA_DOMAIN)
    -S CERT_SUB_DOMAIN      Sub domain to generate the certificat
                            can be set using env var CERT_SUB_DOMAIN
                            (default: $CERT_SUB_DOMAIN so this program will
                             geenrate a certificate for
                             $CERT_SUB_DOMAIN.$CA_DOMAIN)
    -o OUTPUT_DIR           Directory where are generated
                            - CA cert: ca.crt
                            - service certificate: $CERT_SUB_DOMAIN.$CA_DOMAIN.crt
                            - cervice private key: $CERT_SUB_DOMAIN.$CA_DOMAIN.key
                            can be set using env var OUTPUT_DIR
                            (default: $OUTPUT_DIR)
    -G GID                  generated files Group ID owner number
                            can be set using env var GID
                            (default: $GID)
    -U UID                  generated files User ID owner mumber
                            can be set using env var UID
                            (default: $UID)
    -h                      Show this help.
"



while getopts "D:S:G:U:o:h" OPTION
do
    case $OPTION in
        D) CA_DOMAIN=$OPTARG;;
        S) CERT_SUB_DOMAIN=$OPTARG;;
        G) GID=$OPTARG;;
        U) UID=$OPTARG;;
        h) echo "$USAGE";
           exit;;
        *) echo "Unknown parameter... ";
           echo "$USAGE";
           exit 1;;
    esac
done

DOMAIN="$CERT_SUB_DOMAIN.$CA_DOMAIN"

# generate CA
openssl req -new -x509 -extensions v3_ca -newkey rsa:4096 \
    -sha256 \
    -keyout private/ca.key \
    -out certs/ca.crt -nodes \
    -subj "/CN=$CA_DOMAIN" \
    -config ca-config

# geneerate CSR
openssl req -new -nodes -newkey rsa:4096 \
    -sha256 \
    -keyout "private/$DOMAIN.key" \
    -out "$DOMAIN.csr" \
    -subj "/CN=$DOMAIN" \
    -config ca-config

openssl ca -config ca-config -policy policy_anything \
    -extensions server_cert \
    -md sha256 \
    -batch \
    -out "certs/$DOMAIN.crt" \
    -infiles "$DOMAIN.csr"


mkdir -p "$OUTPUT_DIR"
cp "certs/ca.crt" "$OUTPUT_DIR/"
cp "certs/$DOMAIN.crt" "$OUTPUT_DIR/"
cp "private/$DOMAIN.key" "$OUTPUT_DIR/"
chown $UID:$GID -R "$OUTPUT_DIR"
chmod 500 -R "$OUTPUT_DIR"
