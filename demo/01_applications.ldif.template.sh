#!/bin/sh

set -e

USAGE="Usage: $0 -D Root LDAP DC [-h]

Template to generate application test ldif file

Options:
    -D ROOT LDAP DC     The root ldap dc, should looks like "dc=example,dc=com"
    -h                  Show this help.
"


while getopts "D:h" OPTION
do
    case $OPTION in
        D) ROOT_LDAP_DC=$OPTARG;;
        h) echo "$USAGE";
           exit;;
        *) echo "Ignore unknown parameter while generating demo
                 application ldif template" >&2;;
    esac
done


if [[ ! $ROOT_LDAP_DC ]]; then
    echo "Root LDAP DC is required while generating demo application
          ldif template" >&2
    exit 1
fi


cat << EOF
dn: uid=fakeapp,ou=applications,$ROOT_LDAP_DC
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
sn: fakeapp technical user
cn: fakeapp technical user
uid: fakeapp
userPassword: fakeappPASS

dn: uid=fakeapp2,ou=applications,$ROOT_LDAP_DC
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
sn: fakeapp2 technical user
cn: fakeapp2 technical user
uid: fakeapp2
userPassword: fakeapp2PASS

dn: uid=tapp-people-admin,ou=applications,$ROOT_LDAP_DC
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
sn: technical people admin
cn: technical people admin
uid: tapp-people-admin
userPassword: tapp-people-adminPASS
#memberOf: cn=ldap_people_admin,ou=groups,$ROOT_LDAP_DC

dn: uid=tapp-apps-admin,ou=applications,$ROOT_LDAP_DC
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
sn: technical apps admin
cn: technical apps admin
uid: tapp-apps-admin
userPassword: tapp-apps-adminPASS
#memberOf: cn=ldap_people_admin,ou=groups,$ROOT_LDAP_DC
#memberOf: cn=ldap_apps_admin,ou=groups,$ROOT_LDAP_DC

dn: uid=tapp-admin,ou=applications,$ROOT_LDAP_DC
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
sn: technical full admin
cn: technical full admin
uid: tapp-admin
userPassword: tapp-adminPASS
#memberOf: cn=ldap_people_admin,ou=groups,$ROOT_LDAP_DC
#memberOf: cn=ldap_apps_admin,ou=groups,$ROOT_LDAP_DC

EOF
