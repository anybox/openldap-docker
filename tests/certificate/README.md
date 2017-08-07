# Certificat

> **IMPORTANT**: self-signed certificate are not design for production
> use only for testing.

This Dockerfile allow to generate certificate authority (CA) with
a its certificate for a given domain to automate tests that require a
valid certificate.


## Usage

Build that image:

```bash
    docker build -t self-certif .
```


This tool generate the certificate authority and the certificate and its
private key in the ``/certificate`` directory. So you may want to mount
that volume to keep track those files.


```bash
    docker volume create certif
    docker run -it --rm -v certif:/certificate self-certif
```

If you want to check output:

```bash
    docker run -it --rm -v certif:/tmp/certif alpine sh
    / # ls -la /tmp/certif/
    total 24
    drw-------    2 root     root          4096 Feb  1 17:28 .
    drwxrwxrwt    3 root     root          4096 Feb  1 17:28 ..
    -rw-------    1 root     root          1818 Feb  1 17:28 ca.crt
    -rw-------    1 root     root          5467 Feb  1 17:28 ldap.ci.example.com.crt
    -rw-------    1 root     root          1704 Feb  1 17:28 ldap.ci.example.com.key
    / # apk update && apk add openssl
    [...]
    / #  openssl verify -CAfile /tmp/certif/ca.crt /tmp/certif/ldap.ci.example.com.crt 
    /tmp/certif/ldap.ci.example.com.crt: OK
    / # openssl x509 -in certs/webserver.crt -noout -text
    [...]
```

For more information do not miss help option:

```bash
    docker run -it --rm self-certif -h
    Usage: /certificate-authority/entrypoint.sh [-D CA DOMAIN]
                [-S CERT_SUB_DOMAIN] [-o OUTPUT DIR] [-G GROUP ID]
                [-U UID] [-h]
    
    Script to generate CA and certificate for testing purpose.
    
    > **DISCLAIMER**: Generated file should not be used in production server
    
    Options:
        -D CA_DOMAIN            Certificat Authority Domain.
                                can be set using env var CA_DOMAIN
                                (default: ci.example.com)
        -S CERT_SUB_DOMAIN      Sub domain to generate the certificat
                                can be set using env var CERT_SUB_DOMAIN
                                (default: ldap so this program will
                                 geenrate a certificate for
                                 ldap.ci.example.com)
        -o OUTPUT_DIR           Directory where are generated
                                - CA cert: ca.crt
                                - service certificate: ldap.ci.example.com.crt
                                - cervice private key: ldap.ci.example.com.key
                                can be set using env var OUTPUT_DIR
                                (default: /certificate)
        -G GID                  generated files Group ID owner number
                                can be set using env var GID
                                (default: 0)
        -U UID                  generated files User ID owner mumber
                                can be set using env var UID
                                (default: 0)
        -h                      Show this help.
```
