#!/bin/sh

set -e

USAGE="Usage: $0 -D Root LDAP DC -d Domain -o Organization name [-h]

Template to generate organization root tree

Options:
    -D ROOT LDAP DC     The root ldap dc, should looks like dc=example,dc=com
    -d Domain           ldap root domain
    -o Organization     Name of the organization
    -h                  Show this help.
"

while getopts "D:d:o:h" OPTION
do
    case $OPTION in
        D) ROOT_LDAP_DC=$OPTARG;;
        d) DOMAIN=$OPTARG;;
        o) ORGANIZATION=$OPTARG;;
        h) echo "$USAGE";
           exit;;
        *) echo "Ignore unknown parameter while generating
                 organization ldif template" >&2;;
    esac
done

if [[ ! $DOMAIN ]]; then
    echo "DOMAIN is required while generating organization ldif template" >&2
    exit 1
fi

if [[ ! $ROOT_LDAP_DC ]]; then
    echo "Root LDAP DC is required while generating
          organization ldif template" >&2
    exit 1
fi

if [[ ! $ORGANIZATION ]]; then
    echo "ORGANIZATION is required while generating organization
    ldif template" >&2
    exit 1
fi

FIRST_DC=$(echo "$DOMAIN" | sed -e 's/\..*//g')

cat << EOF
dn: $ROOT_LDAP_DC
objectclass: dcObject
objectclass: organization
o: $ORGANIZATION
dc: $FIRST_DC

dn: ou=people,$ROOT_LDAP_DC
objectClass: organizationalUnit
ou: people
description: Physical people that require an account in LDAP

dn: uid=admin,ou=people,$ROOT_LDAP_DC
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
cn: Admin TO REMOVE
displayName: Admin TO REMOVE
sn: Admin TO REMOVE
givenName: Admin TO REMOVE
o: $ORGANIZATION
uid: admin
userPassword: admin
pwdReset: FALSE

dn: ou=groups,$ROOT_LDAP_DC
objectClass: organizationalUnit
ou: groups
description: Group list to create group of people

dn: cn=ldap_admin,ou=groups,$ROOT_LDAP_DC
objectclass: groupOfNames
cn: ldap_admin
description: Ldap user administrators (groups and people)
member: uid=administrator,ou=people,$ROOT_LDAP_DC

# Technical account required by applications
dn: ou=applications,$ROOT_LDAP_DC
objectClass: organizationalUnit
ou: applications
description:
 liste des applications ayant un compte LDAP pour effectuer des
 requêtes. Par défaut ces utilisateurs ont accès en lecture et search tout
 les inetOrgPerson lié aux groupes dont l'entrée InetOrgPerson de l'application
 elle même fait partie.

dn: ou=policies,$ROOT_LDAP_DC
objectClass: organizationalUnit
objectClass: top
ou: policies

EOF