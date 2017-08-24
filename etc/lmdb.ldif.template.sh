#!/bin/sh

set -e

USAGE="Usage: $0 -D Root LDAP DC -P Ldap root password [-h]

Template to generate slapd config file

Options:
    -D ROOT LDAP DC       The root ldap dc, should looks like dc=example,dc=com
    -P Ldap root password The ldap root admin password
    -h                    Show this help.
"

while getopts "D:P:h" OPTION
do
    case $OPTION in
        D) ROOT_LDAP_DC=$OPTARG;;
        P) LDAP_PASSWORD=$OPTARG;;
        h) echo "$USAGE";
           exit;;
        *) echo "Unknown parameter while generating lmdb ldif template" >&2;
           echo "$USAGE" >&2;
           exit 1;;
    esac
done

if [[ ! $ROOT_LDAP_DC ]]; then
    echo "Root LDAP DC is required while generating lmdb ldif template" >&2
    exit 1
fi
if [[ ! $LDAP_PASSWORD ]]; then
    echo "LDAP PASSWORD is required while generating slapd ldif template" >&2
    exit 1
fi

cat << EOF
#######################################################################
# LMDB database definitions
#######################################################################
#
dn: olcDatabase=mdb,cn=config
objectClass: olcDatabaseConfig
objectClass: olcMdbConfig
olcDatabase: mdb
olcSuffix: $ROOT_LDAP_DC
olcRootDN: cn=admin,$ROOT_LDAP_DC
# The database directory MUST exist prior to running slapd AND
# should only be accessible by the slapd and slap tools.
# Mode 700 recommended.
olcDbDirectory: /var/lib/openldap/openldap-data
# Indices to maintain
olcDbIndex: objectClass eq
olcDbIndex: uid         eq,sub
#olcDbIndex: memberof    eq
# Cleartext passwords, especially for the rootdn, should
# be avoided.  See slappasswd(8) and slapd-config(5) for details.
# Use of strong authentication encouraged.
olcRootPW: $LDAP_PASSWORD
# You may want to read the doc before update this file
# http://www.openldap.org/doc/admin24/access-control.html
# This directive allows users to modify their own entries if security
# protections have of strength 128 or better
#olcAccess: {10}
#  to *
#    by ssf=128 self write
#    by ssf=64 anonymous auth
#    by ssf=64 users read
#
# allows users and ldap admin group members to update passwords,
# anonymous users to authenticate against this attribute, and (implicitly)
# denying all access to others
olcAccess: {100}
  to dn.subtree="ou=people,$ROOT_LDAP_DC" attrs=userPassword
    by self write
    by group.exact="cn=ldap_people_admin,ou=groups,$ROOT_LDAP_DC" write
    by anonymous auth
    by * none
# application users and ldap admin group members can not edit user
# application's password
olcAccess: {150}
  to dn.subtree="ou=applications,$ROOT_LDAP_DC" attrs=userPassword
    by group.exact="cn=ldap_apps_admin,ou=groups,$ROOT_LDAP_DC" write
    by self read
    by anonymous auth
    by * none
# Nobody can set memberOf directly, ldap admin members should edit member
# group attribute instead. Application can read memberOf attribute
olcAccess: {200}
  to attrs=memberOf
    by group.exact="cn=ldap_people_admin,ou=groups,$ROOT_LDAP_DC" read
    by dn.subtree="ou=applications,$ROOT_LDAP_DC" read
    by * none
# allow ldap admin to create/write on people sub-tree
# allow ldap application users to read on people sub-tree
# TODO: Could be nice to improve to let applications users read only
# to the revelant group
olcAccess: {300}
  to dn.subtree="ou=people,$ROOT_LDAP_DC"
    by group.exact="cn=ldap_people_admin,ou=groups,$ROOT_LDAP_DC" write
    by dn.subtree="ou=applications,$ROOT_LDAP_DC" read
    by self read
    by * none
olcAccess: {350}
  to dn.subtree="ou=applications,$ROOT_LDAP_DC"
    by group.exact="cn=ldap_apps_admin,ou=groups,$ROOT_LDAP_DC" write
    by self read
    by * none
# Allow ldap admin to manage groups
# Application can read groups as well
olcAccess: {400}
  to dn.subtree="ou=groups,$ROOT_LDAP_DC"
    by group.exact="cn=ldap_people_admin,ou=groups,$ROOT_LDAP_DC" write
    by dn.subtree="ou=applications,$ROOT_LDAP_DC" read
    by * none
# No one can access to policies they should be test and change from the
# main configuration to avoid create security hole
olcAccess: {600}
  to dn.subtree="ou=policies,$ROOT_LDAP_DC"
    by * none
# Allow ldap admin group members to read/write ,$ROOT_LDAP_DC sub tree
# to helps admins task (display the whole tree in Apache active Directory)
olcAccess: {700}
  to dn.subtree="$ROOT_LDAP_DC"
    by group.exact="cn=ldap_people_admin,ou=groups,$ROOT_LDAP_DC" read
    by group.exact="cn=ldap_apps_admin,ou=groups,$ROOT_LDAP_DC" read
    by * none

EOF