#!/bin/sh

set -e

USAGE="Usage: $0 -D Root LDAP DC [-h]

Template to generate groups test ldif file

Options:
    -D ROOT LDAP DC     The root ldap dc, should looks like 'dc=example,dc=com'
    -h                  Show this help.
"


while getopts "D:h" OPTION
do
    case $OPTION in
        D) ROOT_LDAP_DC=$OPTARG;;
        h) echo "$USAGE";
           exit;;
        *) echo "Ignore unknown parameter while generating demo
                 groups ldif template" >&2;;
    esac
done


if [[ ! $ROOT_LDAP_DC ]]; then
    echo "Root LDAP DC is required while generating demo groups
          ldif template" >&2
    exit 1
fi


cat << EOF
dn: cn=fakeapp,ou=groups,$ROOT_LDAP_DC
cn: fakeapp
description: Utilisateur de fakeapp
objectclass: groupOfNames
member: uid=tadministrator,ou=people,$ROOT_LDAP_DC
member: uid=tuser,ou=people,$ROOT_LDAP_DC
EOF
