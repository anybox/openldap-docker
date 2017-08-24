#!/bin/sh

set -e

USAGE="Usage: $0 -d Domain -D ROOT LDAP DC -o Organization [-h]

Template to generate people test ldif file 

Options:
    -D ROOT LDAP DC  The root ldap dc, should looks like "dc=example,dc=com"
    -d Domain        The domain name to generate fake email
    -o Organization     Name of the organization
    -h               Show this help.
"


while getopts "D:d:o:h" OPTION
do
    case $OPTION in
        D) ROOT_LDAP_DC=$OPTARG;;
        d) DOMAIN=$OPTARG;;
        o) ORGANIZATION=$OPTARG;;
        h) echo "$USAGE";
           exit;;
        *) echo "Ignore unknown parameter while generating demo people
                 ldif template" >&2;;
    esac
done


if [[ ! $ROOT_LDAP_DC ]]; then
    echo "Root LDAP DC is required while generating demo people ldif
          template" >&2
    exit 1
fi

if [[ ! $ORGANIZATION ]]; then
    echo "Organization name is required while generating demo people ldif
          template" >&2
    exit 1
fi

if [[ ! $DOMAIN ]]; then
    echo "DOMAIN is required while generating demo people ldif
          template" >&2
    exit 1
fi

cat << EOF
dn: uid=tadmin-people,ou=people,$ROOT_LDAP_DC
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
cn: Test People Administrator
sn: Test People Administrator
givenName: Test People Administrator
mail: tadmin-people@$DOMAIN
mobile: +33600000000
o: $ORGANIZATION
uid: tadmin-people
userPassword: tadmin-peoplePASS
#memberOf: cn=ldap_people_admin,ou=groups,$ROOT_LDAP_DC

dn: uid=tadmin-apps,ou=people,$ROOT_LDAP_DC
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
cn: Test Applications Administrator
sn: Test Applications Administrator
givenName: Test admin apps
mail: tadmin-apps@$DOMAIN
mobile: +33600000000
o: $ORGANIZATION
uid: tadmin-apps
userPassword: tadmin-appsPASS
#memberOf: cn=ldap_apps_admin,ou=groups,$ROOT_LDAP_DC

dn: uid=tadmin,ou=people,$ROOT_LDAP_DC
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
cn: Test Applications & People Administrator
sn: Test Applications & People Administrator
givenName: Test admin
mail: tadmin@$DOMAIN
mobile: +33600000000
o: $ORGANIZATION
uid: tadmin
userPassword: tadminPASS
#memberOf: cn=ldap_apps_admin,ou=groups,$ROOT_LDAP_DC
#memberOf: cn=ldap_people_admin,ou=groups,$ROOT_LDAP_DC

dn: uid=tuser,ou=people,$ROOT_LDAP_DC
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
cn: Test User
sn: User
givenName: Test User
mail: tuser@$DOMAIN
mobile: +33600000000
o: $ORGANIZATION
uid: tuser
userPassword: tuserPASS
memberOf: cn=fakeapp,ou=groups,$ROOT_LDAP_DC

dn: uid=tuser2,ou=people,$ROOT_LDAP_DC
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
cn: Test User 2
sn: User 2
givenName: Test User 2
mail: tuser@$DOMAIN
mobile: +33600000000
o: $ORGANIZATION
uid: tuser2
userPassword: tuser2PASS

dn: uid=tdisableduser,ou=people,$ROOT_LDAP_DC
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
cn: Test Disabled User
sn: Disabled User
givenName: Test disabled user
mail: tdisableduser@$DOMAIN
mobile: +33600000000
o: $ORGANIZATION
uid: tdisableduser
userPassword: tdisableduserPASS
pwdAccountLockedTime: 000001010000Z

dn: uid=tnopassuser,ou=people,$ROOT_LDAP_DC
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
cn: Test No Password User
sn: No Password User
givenName: Test no password
mail: tdisableduser@$DOMAIN
mobile: +33600000000
o: $ORGANIZATION
uid: tnopassuser
EOF
