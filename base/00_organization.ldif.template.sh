#!/bin/sh

set -e

USAGE="Usage: $0 -D Root LDAP DC -d Domain -o Organization name
                 -u ldap admin uid -p ldap admin password [-h]

Template to generate organization root tree

Options:
    -D ROOT LDAP DC        The root ldap dc, should looks like dc=example,dc=com
    -d Domain              ldap root domain
    -o Organization        Name of the organization
    -u ldap admin uid      Ldap default administrator (the one under ou=people)
    -p ldap admin password Ldap administrator password (for the given above uid)
    -h                     Show this help.
"

while getopts "D:d:o:p:u:h" OPTION
do
    case $OPTION in
        D) ROOT_LDAP_DC=$OPTARG;;
        d) DOMAIN=$OPTARG;;
        o) ORGANIZATION=$OPTARG;;
        u) ADMIN_UID=$OPTARG;;
        p) ADMIN_PASS=$OPTARG;;
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

if [[ ! $ADMIN_UID ]]; then
    echo "Administrator uid is required while generating organization
    ldif template" >&2
    exit 1
fi

if [[ ! $ADMIN_PASS ]]; then
    echo "Administrator PASSWORD is required while generating organization
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

dn: uid=$ADMIN_UID,ou=people,$ROOT_LDAP_DC
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
cn: Admin TO REMOVE
displayName: Admin TO REMOVE
sn: Admin TO REMOVE
givenName: Admin TO REMOVE
o: $ORGANIZATION
uid: $ADMIN_UID
userPassword: $ADMIN_PASS
pwdReset: FALSE

dn: ou=groups,$ROOT_LDAP_DC
objectClass: organizationalUnit
ou: groups
description: Group list to create group of people

dn: cn=ldap_people_admin,ou=groups,$ROOT_LDAP_DC
objectclass: groupOfNames
cn: ldap_people_admin
description: Ldap user administrators (ou=groups and ou=people)
member: uid=$ADMIN_UID,ou=people,$ROOT_LDAP_DC

dn: cn=ldap_apps_admin,ou=groups,$ROOT_LDAP_DC
objectclass: groupOfNames
cn: ldap_apps_admin
description: Ldap application user administrators(ou=applications)
member: uid=$ADMIN_UID,ou=people,$ROOT_LDAP_DC

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