# docker ldap

This project aims to setup OpenLdap in alpine Docker container.

It provide a default configuration and aims to give some tools to
upgrade changes between 2 versions.

It's probably easier for you to fork this repo if you don't like
those settings but like how it's administrate and test.

Quick Start
-----------

requirements:

- DNS point to your ldap server (here **ldap.example.org**)
- You have a certificate for that domain (``ldap.example.org.crt`` and
  ``ldap.example.crt.key``), to generate [Let's Encrypt Certificate](
  https://letsencrypt.org/) you could use [cerbot in docker](
  https://github.com/petrus-v/certbot)

Then you have to:

* First run only, setup ldap configuration and base config
* Restart server, test, add user, change administrator configuration
* Setup your first apache service and required configuration



## Default ldap configuration

In this chapter I'll give a short how we have organized default
configuration and rules that are [tests (using python unitest)](
tests/test_ldap.py)

Let's say you have configure ``DOMAINE=example.com`` you will get
the following tree.

```
dc: com
├── dc=example
│   ├── cn=admin                # Root ldap account
│   ├── ou=people               # Where users are saved
│   │   ├── uid=admin           # Default user administrator
│   │   ├── uid=user 1
│   │   ├── uid=...
│   │   └── uid=user n
│   ├── groups                  # Group definition
│   │   ├── cn=ldap_admin       # Ldap account administrator
│   │   ├── cn=group 1
│   │   ├── cn=...
│   │   └── cn=group n
│   ├── applications            # Application/service account
│   │   ├── uid=app 1
│   │   ├── uid=...
│   │   └── uid=app2 n
│   ├── policies                # Ldap policies (about passwords)
│   │   └── cn=default
```

Bellow the list of user me may met:

* Anonymous
* User account
* Ldap adminstrator (those linked to ldap_admin group)
* The root ldap administrator
* Application/service user account & Groups


### Anonymous connexion

Anonymous account are only able to be inveted to connect themself.


### User account

Any user entry under ``ou=people,dc=example,dc=com``

Users can read their own entry and change their own password, they
can't read other users information or change other informations.


### Ldap administrator

Users that administrate following entries in ldap:

* people
* groups
* applications


Those users must have an entry in ``ou=people,dc=example,dc=com``
and be a member of ``cn=ldap_admin,ou=groups,dc=example,dc=com``
group.


They are allowed to:

* Create new ``inetOrgPerson`` entry under 
  ``ou=people,dc=example,dc=com`` for user account.
* Can update thoses people(users) entries (passwords as well)
* Create new group entry under ``ou=groups,dc=example,dc=com``
* Add members in groups
* Create new application entry under
  ``ou=applications,dc=example,dc=com``

So they can do almost whaterver they want under
``dc=example,dc=com``.


### Ldap root account

This account should be used only in automated way while deploying
a new version, this user can do anything on LDAP. But to ensure
tested rules still correct you should'nt change them directly.
 

### Application account & Groups

Application user account (under
``ou=applications,dc=example,dc=com``) are allowed to read group
members ``ou=groups,dc=example,dc=com`` (ie: likes the Apache 
``Require ldap-goup`` directive) and read user lists (children of
``ou=people,dc=example,dc=com``) to allow to process the search.


## Persistent data


For OpenLDAP every thing are data configuration (stored in
``/etc/openldap/slapd.d``) user accounts (stored in
``var/lib/openldap/openldap-data``).

This allow to change OpenLDAP while running, this is nice feature
but could be dangerous if you are changing configuration that you
haven't tested, you can easly create a security hole in your ldap.

## Install - update - upgrade


TODO: handle version number diff to handle upgrade between versions

## Let's encrypt certificate


TODO:


- [ ] tool to generate or add application entry (or make possible to
      administrator to setup application, or add application admin
      group)
- [ ] document certificate access uid ldap == 666
- [ ] manage & document active/inactive users
- [ ] Add volumes? json? to init user data the first time
- [ ] allow runing batch createion
- [ ] test password policies?
- [ ] add a tool to generate init user/application/group accounts
- [ ] test restarting CR / test with mapped volume
- [ ] test upgrade version
- [ ] http://www.openldap.org/doc/admin24/security.html
- [ ] retrouver la ressource qui parle de lanceur d'application dans
      docker
- [ ] automatiser le renouvellement de certificat avec let's encrypt
      + restart openldap

