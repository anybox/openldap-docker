#!/bin/sh

# PV I'm not sure this issue still true as long we are using docker 1.12 or
# higher and some version of openLdap has been released since that happen
# so comment to keep an eye on it in case of memory issue:
# When not limiting the open file descriptors limit, the memory consumption of
# slapd is absurdly high. See https://github.com/docker/docker/issues/8231
# ulimit -n 8192

set -e
set +x

PASS=`< /dev/urandom tr -dc _A-Za-z0-9~\&\(\)\^$%,?\;. | head -c 32;echo`
SSHA_PASS=`slappasswd -ns $PASS`

LDAP_ROOT_PASSWORD=${LDAP_ROOT_PASSWORD:-$SSHA_PASS}
LDAP_LOG_LEVEL=${LDAP_LOG_LEVEL:-64}
LDAP_DEFAULT_ADMIN_UID=${LDAP_DEFAULT_ADMIN_UID:-"administrator"}
LDAP_DEFAULT_ADMIN_PASSWORD=${LDAP_DEFAULT_ADMIN_PASSWORD:-`slappasswd -ns "Change Me!"`}
DOMAIN=${DOMAIN:-example.com}
ORGANIZATION=${ORGANIZATION:-"Example corporation"}
LDAP_SUB_DOMAIN=${LDAP_SUB_DOMAIN:-ldap}
LDAP_CA_CERTIFICATE_PATH=${LDAP_CA_CERTIFICATE_PATH:-false}
LDAP_CERTIFICATE_PATH=${LDAP_CERTIFICATE_PATH:-/ssl/$LDAP_SUB_DOMAIN.$DOMAIN.crt}
LDAP_CERTIFICATE_KEY_PATH=${LDAP_CERTIFICATE_KEY_PATH:-/ssl/$SUB_DOMAIN.$DOMAIN.key}

USAGE="Usage: $0 [-C COMMAND [params [params [...]]] [-P Root Password] [-h]
                 [-u Default administrator uid] [-p Default admin password]
                 [-L LOG_LEVEL] [-a CA_FILE_PATH] [-D Domain] [-d sub-domain]
                 [-O Organization]
Wrapper entry point script to setup and run OpenLdap

Options:
    -C COMMAND      Special command to by pass this entry point, if provide
                    it run the given command with all given params, it can only
                    be used alone
    -D DOMAIN       Define domain, which is used for the ldap configuration,
                    example.com becomes dc=example,dc=com (default: $DOMAIN)
    -O ORGANIZATION Name of the organization (default: $ORGANIZATION)
    -d SUB DOMAIN   sub domain to compose the url used to access to to that ldap.
                    ldaps://$LDAP_SUB_DOMAIN.$DOMAIN. (default: $LDAP_SUB_DOMAIN)
    -P PASSWORD     Define admin root ldap password, used only while setting up
                    the ldap config volume (default: $LDAP_ROOT_PASSWORD).
                    This can be set using environment LDAP_ROOT_PASSWORD.
                    use slappasswd -s secret to generate a SSHA password and use
                    the whole output (ie: {SSHA}TjUaNY5sTf//mwqKl3WeI37NKsa5cTa9)
    -u ADMIN UID    Default ldap user administrator uid (will be under
                    uid=$LDAP_DEFAULT_ADMIN_UID,ou=people,dc=example,dc=com)
                    (default value: $LDAP_DEFAULT_ADMIN_UID)
    -p ADMIN PASS   Password for given admin uid $LDAP_DEFAULT_ADMIN_PASSWORD
                    (default: $LDAP_DEFAULT_ADMIN_PASSWORD)
    -L LOG LEVEL    ldap deamon log level
                    Can also be set through environement variable LDAP_LOG_LEVEL
                    (default: $LDAP_LOG_LEVEL)
    -a CA FILE      ldap Certificate Authority file path
                    Can also be set through environement variable
                    LDAP_CA_CERTIFICATE_PATH
                    (default: $LDAP_CA_CERTIFICATE_PATH)
    -c Certif       Certificate file path
                    Can also be set through environement variable
                    LDAP_CERTIFICATE_PATH
                    (default: $LDAP_CERTIFICATE_PATH)
    -k Certif       Certificate private key file path
                    Can also be set through environement variable
                    LDAP_CERTIFICATE_KEY_PATH
                    (default: $LDAP_CERTIFICATE_KEY_PATH)
    -h              Show this help.
"


while getopts "C:P:L:a:c:k:d:D:O:p:u:h" OPTION
do
    case $OPTION in
        C) if [[ $1 == "-C" ]]; then
                shift
                exec "$@"
                exit
           fi;
           echo "-C must be the first param.";
           echo "$USAGE";
           exit 1;;
        P) LDAP_ROOT_PASSWORD=$OPTARG;;
        u) LDAP_DEFAULT_ADMIN_UID=$OPTARG;;
        p) LDAP_DEFAULT_ADMIN_PASSWORD=$OPTARG;;
        D) DOMAIN=$OPTARG;;
        O) ORGANIZATION=$OPTARG;;
        d) LDAP_SUB_DOMAIN=$OPTARG;;
        L) LDAP_LOG_LEVEL=$OPTARG;;
        a) LDAP_CA_CERTIFICATE_PATH=$OPTARG;;
        c) LDAP_CERTIFICATE_PATH=$OPTARG;;
        k) LDAP_CERTIFICATE_KEY_PATH=$OPTARG;;
        h) echo "$USAGE";
           exit;;
        *) echo "Unknown parameter... ";
           echo "$USAGE";
           exit 1;;
    esac
done

LDAP_ROOT_DC="dc=$(echo "$DOMAIN" | sed -e 's/\./,dc=/g')"

function import_files {
    # Import ldif files or *.ldif.template.sh files found in a directory
    # import in an alphabetic order (based on ``ls``)
    # $1: directory to use
    # $2: remove directory after import, if value equals "Yes" then
    directory=$1
    dir_to_remove=$2
    if [[ -d "$directory" ]]; then

        for file in `ls $directory*.ldif.template.sh`; do
            output=${file%.template.sh}
            echo "generate $output from template: $file"
            $file -D "$LDAP_ROOT_DC" \
                  -d "$DOMAIN" \
                  -o "$ORGANIZATION" \
                  -u "$LDAP_DEFAULT_ADMIN_UID" \
                  -p "$LDAP_DEFAULT_ADMIN_PASSWORD" > $output
        done
        for file in `ls $directory*.ldif`; do
            echo "Import init data: $file"
            slapadd -d $LDAP_LOG_LEVEL -F /etc/openldap/slapd.d/ -l "$file"
        done
        if [ "$dir_to_remove" = true ]; then
            rm -r "$directory"
        fi
    fi
}

if [[ -d "/etc/openldap/slapd.d/cn=config" ]]; then
    echo "LDAP Config volumes already setup!"
else
    echo "Génerate slapd.ldif from templates"
    /etc/openldap/slapd.ldif.template.sh \
        -C $LDAP_CERTIFICATE_PATH \
        -K $LDAP_CERTIFICATE_KEY_PATH \
        -A $LDAP_CA_CERTIFICATE_PATH > /etc/openldap/slapd.ldif
    /etc/openldap/lmdb.ldif.template.sh \
        -P $LDAP_ROOT_PASSWORD \
        -D $LDAP_ROOT_DC >> /etc/openldap/slapd.ldif
    /etc/openldap/overlay_settings.ldif.template.sh \
        -D $LDAP_ROOT_DC  \
        -u "$LDAP_DEFAULT_ADMIN_UID" >> /etc/openldap/slapd.ldif

    echo "import slapd.ldif"
    cat /etc/openldap/slapd.ldif
    slapadd -d $LDAP_LOG_LEVEL -n0 -F /etc/openldap/slapd.d/ \
            -l /etc/openldap/slapd.ldif
fi

if [[ -f "/var/lib/openldap/openldap-data/data.mdb" ]]; then
    echo "LDAP DATA volume already exists!"
    # TODO: execute ldap modify according update version mecanism to define
    # import_files /srv/ldap/init/
else
    import_files /etc/openldap/root_data/ true
    import_files /srv/ldap/init/ false
    import_files /srv/ldap/demo/ false
fi

echo "Make slapd.d own and only usable by ldap user"
chown -R ldap:ldap /etc/openldap/slapd.d/
chmod -R 500 /etc/openldap/slapd.d/
chown ldap:ldap -R /var/lib/openldap

echo "Run slapd..."
# exec slapd to give it PID 1 (otherwise signals are not sent properly)
exec slapd -d $LDAP_LOG_LEVEL -F /etc/openldap/slapd.d -u ldap -g ldap -h "ldaps://"
