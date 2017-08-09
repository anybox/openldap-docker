#!/bin/sh

set -e

USAGE="Usage: $0 -D Root LDAP DC [-h]

Template to generate slapd config file

Options:
    -D ROOT LDAP DC     The root ldap dc, should looks like dc=example,dc=com
    -h                  Show this help.
"

while getopts "D:h" OPTION
do
    case $OPTION in
        D) ROOT_LDAP_DC=$OPTARG;;
        h) echo "$USAGE";
           exit;;
        *) echo "Unknown parameter while generating overlay ldif template" >&2;
           echo "$USAGE" >&2;
           exit 1;;
    esac
done

if [[ ! $ROOT_LDAP_DC ]]; then
    echo "Root LDAP DC is required while generating overlay ldif template" >&2
    exit 1
fi

cat << EOF
dn: olcOverlay=memberof,olcDatabase={1}mdb,cn=config
objectClass: olcConfig
objectClass: olcMemberOf
objectClass: olcOverlayConfig
objectClass: top
olcOverlay: memberof
olcMemberOfDangling: drop
olcMemberOfRefInt: TRUE
olcMemberOfGroupOC: groupOfNames
olcMemberOfMemberAD: member
olcMemberOfMemberOfAD: memberOf

dn: olcOverlay=refint,olcDatabase={1}mdb,cn=config
objectClass: olcConfig
objectClass: olcOverlayConfig
objectClass: olcRefintConfig
objectClass: top
olcOverlay: refint
olcRefintAttribute: memberOf member

dn: olcOverlay=ppolicy,olcDatabase={1}mdb,cn=config
objectClass: olcConfig
objectClass: olcOverlayConfig
objectClass: olcPPolicyConfig
objectClass: top
olcOverlay: ppolicy
olcPPolicyDefault: cn=default,ou=policies,$ROOT_LDAP_DC
olcPPolicyHashCleartext: FALSE
olcPPolicyUseLockout: FALSE
olcPPolicyForwardUpdates: FALSE

EOF
