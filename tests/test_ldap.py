"""This test case is used to test LDAP configuration

This heavily used inheritance mechanisms to avoid duplication code. Where
a class was created by kind of users (Anonymous, normal user, application user,
ldap administrator, root ldap administrator)

So for instance ``def test_search(self):`` is implemented for anonymous user
for ldap users as long it's not overwritten the same assertions will occurs.
Then ldap administrator (those user member of the ldap_admin group) can
search over the ldap so the method was overwritten

So we can draw a Class Tree which currently looks like
-
. TestLdapAnonymous
├── TestLdapApplicationUser
└── TestLdapUser
    └── TestLdapAdministrator
        └── TestRootLdapAdmin

"""
import os

from contextlib import contextmanager
from ldap3 import Server, Connection, ALL, MODIFY_REPLACE, MODIFY_ADD
from ldap3.extend.standard.modifyPassword import ModifyPassword
from subprocess import check_call, CalledProcessError
from unittest import TestCase
from uuid import uuid4

LDAP_HOST = os.getenv("LDAP_HOST", 'ldaps://ldap.ci.example.com')
ROOT_LDAP_SECRET = os.getenv("ROOT_LDAP_SECRET", "secret")
ROOT_DC = os.getenv("ROOT_DC", "dc=ci,dc=example,dc=com")
ROOT_LDAP_DN = os.getenv("ROOT_LDAP_DN", "cn=admin,") + ROOT_DC
ORGANIZATION = os.getenv("ORGANIZATION", "example corporate")
NEW_PASSWORD = "sofdij%*/6548994"


@contextmanager
def ldap_connection(dn=None, password=None, con_params=None, serv_params=None):
    if not con_params:
        con_params = {
            'auto_bind': True
        }
    if dn:
        con_params['user'] = dn
    if password:
        con_params['password'] = password
    if not serv_params:
        serv_params = {'get_info': ALL}
    server = Server(LDAP_HOST, **serv_params)
    connection = Connection(server, **con_params)
    yield connection
    connection.unbind()


class TestLdapAnonymous(TestCase):

    def setUp(self):
        super(TestLdapAnonymous, self).setUp()
        self.user_dn = ''
        self.user_pass = ''

    def test_update_own_attribute(self):
        # manage special anonymouos use case
        update_dn = self.user_dn
        if not update_dn:
            update_dn = "uid=tuser,ou=people," + ROOT_DC
        with ldap_connection(dn=self.user_dn, password=self.user_pass) as con:
            self.assertFalse(
                con.modify(
                    update_dn,
                    {'cn': [(MODIFY_REPLACE, ['Name change'])]}),
                con.result
            )
        with ldap_connection(
                dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
        ) as root_con:
            root_con.search(
                update_dn,
                '(objectclass=inetOrgPerson)',
                attributes=['cn']
            )
            self.assertNotEqual(
                "Name change",
                root_con.entries[0].cn.value
            )

    def test_search(self):
        with ldap_connection(dn=self.user_dn, password=self.user_pass) as con:
            self.assertFalse(
                con.search('' + ROOT_DC, '(objectclass=*)')
            )
            self.assertFalse(con.entries)
            self.assertFalse(
                con.search(
                    'ou=people,' + ROOT_DC,
                    '(objectclass=inetOrgPerson)'
                ),
                con.result
            )
            self.assertFalse(con.entries)
            self.assertFalse(
                con.search(
                    'ou=people,' + ROOT_DC,
                    '(& (objectclass=inetOrgPerson)'
                    '   (memberOf=cn=fakeapp,ou=groups,' + ROOT_DC + '))'
                ),
                con.result
            )
            self.assertFalse(con.entries)
            self.assertFalse(
                con.search('ou=groups,' + ROOT_DC, '(objectclass=*)'),
                con.result
            )
            self.assertFalse(con.entries)
            self.assertFalse(
                con.search(
                    'ou=applications,' + ROOT_DC,
                    '(objectclass=*)'
                ),
                con.result
            )
            self.assertFalse(con.entries)
            if self.user_dn:
                self.assertFalse(
                    con.search(self.user_dn, '(objectclass=inetOrgPerson)')
                )

    def test_create_user(self):
        self.assertCreateLdapUserWithCurrentUser(self.assertFalse)

    def assertCreateLdapUserWithCurrentUser(self, assertion):
        with ldap_connection(dn=self.user_dn, password=self.user_pass) as con:
            return self.assertCreateLdapUser(con, assertion)

    def assertCreateLdapUser(self, connection, assertion):
        user_uid = "user-%s" % uuid4()
        user_dn = 'uid=%s,ou=people,%s' % (user_uid, ROOT_DC)
        assertion(
            connection.add(
                user_dn,
                'inetOrgPerson',
                {
                    'cn': 'Fake User',
                    'sn': 'Fake',
                    'mobile': 1111,
                    'givenName': 'User',
                    'o': ORGANIZATION,
                    'uid': user_uid,
                }
            ),
            connection.result
        )
        return user_dn

    def test_create_group(self):
        with ldap_connection(dn=self.user_dn, password=self.user_pass) as con:
            self.assertCreateLdapGroup(con, self.assertFalse)

    def assertCreateLdapUserApplication(self, connection, assertion):
        """
        dn: uid=cloud,ou=applications,+ ROOT_DC
        objectClass: person
        objectClass: organizationalPerson
        objectClass: inetOrgPerson
        sn: Cloud technical user
        cn: Cloud technical user
        uid: cloud
        userPassword: cloudPASS
        """
        app_uid = "app-%s" % uuid4()
        app_dn = 'uid=%s,ou=applications,%s' % (app_uid, ROOT_DC)
        assertion(
            connection.add(
                app_dn,
                'inetOrgPerson',
                {
                    'cn': 'Fake application',
                    'sn': 'Fake application',
                    'uid': app_uid,
                    'userPassword': 'Fake Pass %s' % app_uid,
                }
            ),
            connection.result
        )
        return app_dn

    def assertCreateLdapGroup(self, connection, assertion, members=None):
        """
            dn: cn=cloud,ou=groups,+ ROOT_DC
            cn: cloud
            description: Utilisateur du cloud système de partage de fichier
            objectclass: groupOfNames
            member: uid=tuser,ou=people,+ ROOT_DC
        """
        if not members:
            members = ['uid=tuser,ou=people,' + ROOT_DC]
        group_cn = "group-%s" % uuid4()
        group_dn = 'cn=%s,ou=groups,%s' % (group_cn, ROOT_DC)
        assertion(
            connection.add(
                group_dn,
                'groupOfNames',
                {
                    'cn': group_cn,
                    'description': 'test group',
                    'member': members,
                }
            ),
            connection.result
        )
        return group_dn

    def test_grant_user_to_group(self):
        self.assertGrantUserToGroup(self.assertFalse)

    def assertGrantUserToGroup(self, assertion):
        with ldap_connection(
            dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
        ) as con:
            user_dn = self.assertCreateLdapUser(con, self.assertTrue)
            group_dn = self.assertCreateLdapGroup(con, self.assertTrue)

        with ldap_connection(dn=self.user_dn, password=self.user_pass) as con:
            assertion(
                con.modify(
                    group_dn,
                    {'member': [(MODIFY_ADD, [user_dn, ])]}
                ),
                con.result
            )
        with ldap_connection(
                dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
        ) as con:
            con.search(
                user_dn,
                '(objectClass=inetOrgPerson)',
                attributes=['memberOf']
            ),
            if con.entries and con.entries[0].memberOf:
                assertion(
                    group_dn in con.entries[0].memberOf.value,
                    "%r not in %r" % (group_dn, con.entries[0].memberOf.value)
                )

    def test_edit_memberof_forbidden(self):
        # Editing memberof attrs should be forbiden as long `refint overlay
        # <http://www.openldap.org/doc/admin24/
        # overlays.html#Referential%20Integrity>`_ currently is not able to
        # add member attributes on the corresponding groups (not sure if it's
        # a wrong setting or overlay limitation). As long overlay can be
        # configured differently per replicate I guess this is an overlay
        # implementation choice... Anyway at the moment we make sure we do not
        # change memberOf attribute
        with ldap_connection(
            dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
        ) as con:
            user_dn = self.assertCreateLdapUser(con, self.assertTrue)
            group_dn = self.assertCreateLdapGroup(con, self.assertTrue)
        with ldap_connection(dn=self.user_dn, password=self.user_pass) as con:
            self.assertFalse(
                con.modify(
                    user_dn,
                    {'memberOf': [(MODIFY_ADD, [group_dn, ])]}
                ),
                con.result
            )

    def prepare_tests(self):
        with ldap_connection(
            dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
        ) as con:
            user_dn = self.assertCreateLdapUser(con, self.assertTrue)
            group_dn = self.assertCreateLdapGroup(con, self.assertTrue)
            app_dn = self.assertCreateLdapUserApplication(
                con, self.assertTrue
            )
        return {
            'user': [self.assertFalse, user_dn, "uid=user-%s" % uuid4()],
            'group': [self.assertFalse, group_dn, "cn=group-%s" % uuid4()],
            'application': [self.assertFalse, app_dn, "cn=app-%s" % uuid4()],
        }

    def test_rename_entry(self):
        renames = self.prepare_tests()
        with ldap_connection(dn=self.user_dn, password=self.user_pass) as con:
            for assertion, old_dn, new_dn in renames.values():
                assertion(
                    con.modify_dn(old_dn, new_dn)
                )

    def test_create_application_user(self):
        with ldap_connection(dn=self.user_dn, password=self.user_pass) as con:
            self.assertCreateLdapUserApplication(
                con, self.assertFalse
            )

    def test_remove_entries(self):
        removes = self.prepare_tests()
        with ldap_connection(dn=self.user_dn, password=self.user_pass) as con:
            for assertion, old_dn, _ in removes.values():
                assertion(
                    con.delete(old_dn)
                )

    def assertChangePassword(
        self, con, assertion, user_dn, old_pass, new_pass
    ):
        ModifyPassword(
            con, user=user_dn,  old_password=old_pass, new_password=new_pass
        ).send()
        assertion(
            con.result['description'] == "success",
            con.result
        )

    def test_change_other_people_password(self):
        with ldap_connection(dn=self.user_dn, password=self.user_pass) as con:
            self.assertChangePassword(
                con,
                self.assertFalse,
                'uid=tuser2,ou=people,' + ROOT_DC,
                'tuser2PASS',
                NEW_PASSWORD
            )

    def test_change_application_password(self):
        with ldap_connection(dn=self.user_dn, password=self.user_pass) as con:
            self.assertChangePassword(
                con,
                self.assertFalse,
                'uid=fakeapp,ou=applications,' + ROOT_DC,
                'fakeappPASS',
                NEW_PASSWORD
            )

    # def test_do_not_change_other_people_info(self):
    #     self.fail("not implemented")


class TestLdapApplicationUser(TestLdapAnonymous):

    def setUp(self):
        super(TestLdapApplicationUser, self).setUp()
        self.user_dn = "uid=fakeapp2,ou=applications," + ROOT_DC
        self.user_pass = 'fakeapp2PASS'

    def test_search(self):
        with ldap_connection(dn=self.user_dn, password=self.user_pass) as con:
            self.assertFalse(
                con.search(ROOT_DC, '(objectclass=*)')
            )
            self.assertFalse(con.entries)
            self.assertTrue(
                con.search(
                    'ou=people,' + ROOT_DC,
                    '(objectclass=inetOrgPerson)'
                ),
                con.result
            )
            self.assertTrue(con.entries)
            self.assertTrue(
                con.search(
                    'ou=groups,' + ROOT_DC,
                    '(member=uid=tuser,ou=people,' + ROOT_DC + ')'
                ),
                con.result
            )
            self.assertTrue(con.entries)
            self.assertTrue(
                con.search(
                    'ou=people,' + ROOT_DC,
                    '(& (objectclass=inetOrgPerson)'
                    '   (memberOf=cn=fakeapp,ou=groups,' + ROOT_DC + '))'
                ),
                con.result
            )
            self.assertTrue(con.entries)
            self.assertFalse(
                con.search(
                    'ou=applications,' + ROOT_DC,
                    '(objectclass=*)'
                ),
                con.result
            )
            self.assertFalse(con.entries)
            if self.user_dn:
                self.assertFalse(
                    con.search(self.user_dn, '(objectclass=inetOrgPerson)')
                )


class TestLdapUser(TestLdapAnonymous):

    def setUp(self):
        super(TestLdapUser, self).setUp()
        self.user_dn = "uid=tuser,ou=people," + ROOT_DC
        self.user_pass = 'tuserPASS'

    def test_search(self):
        with ldap_connection(dn=self.user_dn, password=self.user_pass) as con:
            self.assertFalse(
                con.search(ROOT_DC, '(objectclass=*)')
            )
            self.assertFalse(con.entries)
            self.assertFalse(
                con.search(
                    'ou=people,' + ROOT_DC,
                    '(objectclass=inetOrgPerson)'
                ),
                con.result
            )
            self.assertFalse(con.entries)
            self.assertFalse(
                con.search(
                    'ou=people,' + ROOT_DC,
                    '(& (objectclass=inetOrgPerson)'
                    '   (memberOf=cn=fakeapp,ou=groups,' + ROOT_DC + '))'
                ),
                con.result
            )
            self.assertFalse(con.entries)
            self.assertFalse(
                con.search('ou=groups,' + ROOT_DC, '(objectclass=*)'),
                con.result
            )
            self.assertFalse(con.entries)
            self.assertFalse(
                con.search(
                    'ou=applications,' + ROOT_DC,
                    '(objectclass=*)'
                ),
                con.result
            )
            self.assertFalse(con.entries)
            if self.user_dn:
                self.assertTrue(
                    con.search(self.user_dn, '(objectclass=inetOrgPerson)')
                )

    def test_change_owns_password(self):
        def reset_password():
            with ldap_connection(
                    dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
            ) as con:
                # set password back
                self.assertTrue(
                    con.modify(
                        self.user_dn,
                        {'userPassword': [(MODIFY_REPLACE, [self.user_pass])]}
                    ),
                    con.result
                )

        self.addCleanup(reset_password)

        with ldap_connection(dn=self.user_dn, password=self.user_pass) as con:
            self.assertChangePassword(
                con,
                self.assertTrue,
                self.user_dn,
                self.user_pass,
                NEW_PASSWORD
            )


class TestLdapAdministrator(TestLdapUser):

    def setUp(self):
        super(TestLdapAdministrator, self).setUp()
        self.user_dn = "uid=tadministrator,ou=people," + ROOT_DC
        self.user_pass = 'tadministratorPASS'
        self.grant_ldap_admin_group()

    def prepare_tests(self):
        renames = super(TestLdapAdministrator, self).prepare_tests()
        renames['user'][0] = self.assertTrue
        renames['group'][0] = self.assertTrue
        renames['application'][0] = self.assertTrue
        return renames

    def test_create_application_user(self):
        with ldap_connection(dn=self.user_dn, password=self.user_pass) as con:
            self.assertCreateLdapUserApplication(
                con, self.assertTrue
            )

    def test_create_group(self):
        with ldap_connection(dn=self.user_dn, password=self.user_pass) as con:
            self.assertCreateLdapGroup(con, self.assertTrue)

    def grant_ldap_admin_group(self):
        ldap_admin_group_dn = 'cn=ldap_admin,ou=groups,' + ROOT_DC
        search_filter = "(&(objectclass=inetOrgPerson)(memberof=%s))" % \
                        ldap_admin_group_dn
        with ldap_connection(
            dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
        ) as root_con:
            root_con.search(
                self.user_dn, search_filter, attributes=['memberOf']
            )
            if len(root_con.entries) == 0:
                root_con.modify(
                    ldap_admin_group_dn,
                    {'member': [(MODIFY_ADD, [self.user_dn, ])]}
                )
                root_con.search(
                    self.user_dn, search_filter, attributes=['memberOf']
                )
            self.assertTrue(
                ldap_admin_group_dn in root_con.entries[0].memberOf.value,
                "%r not in %r" % (
                    ldap_admin_group_dn,
                    root_con.entries[0].memberOf.value
                )
            )

    def test_search(self):
        with ldap_connection(dn=self.user_dn, password=self.user_pass) as con:
            self.assertTrue(
                con.search('ou=people,' + ROOT_DC, '(objectClass=*)')
            )
            self.assertTrue(con.entries)
            self.assertTrue(
                con.search('ou=groups,' + ROOT_DC, '(objectClass=*)')
            )
            self.assertTrue(con.entries)
            self.assertTrue(
                con.search(
                    'ou=people,' + ROOT_DC,
                    '(& (objectclass=inetOrgPerson)'
                    '   (memberOf=cn=fakeapp,ou=groups,' + ROOT_DC + '))'
                ),
                con.result
            )
            self.assertTrue(con.entries)
            self.assertTrue(
                con.search(
                    'ou=applications,' + ROOT_DC,
                    '(objectClass=*)'
                ),
                con.result
            )
            self.assertTrue(con.entries)

    def test_create_user(self):
        self.assertCreateLdapUserWithCurrentUser(self.assertTrue)

    def test_update_own_attribute(self):
        with ldap_connection(dn=self.user_dn, password=self.user_pass) as con:
            self.assertTrue(
                con.modify(
                    self.user_dn,
                    {'cn': [(MODIFY_REPLACE, ['Name change'])]}),
                con.result
            )
        with ldap_connection(
                dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
        ) as root_con:
            root_con.search(
                self.user_dn,
                '(objectclass=inetOrgPerson)',
                attributes=['cn']
            )
            self.assertEqual(
                "Name change",
                root_con.entries[0].cn.value
            )

    def test_grant_user_to_group(self):
        self.assertGrantUserToGroup(self.assertTrue)

    def test_memberof_rename_user_entry(self):
        """This test ensure `refint overlay <http://www.openldap.org/doc/
        admin24/overlays.html#Referential%20Integrity>`_ is properly set

        while moving user or removing users, make sure groups get update
        """
        with ldap_connection(
                dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
        ) as con:
            user_dn = self.assertCreateLdapUser(con, self.assertTrue)
            group_dn = self.assertCreateLdapGroup(
                con, self.assertTrue, members=[user_dn]
            )
        with ldap_connection(dn=self.user_dn, password=self.user_pass) as con:
            new_uid = "uid=user-%s" % uuid4()
            new_dn = '%s,ou=people,%s' % (new_uid, ROOT_DC)
            self.assertTrue(con.modify_dn(user_dn, new_uid), con.result)
            con.search(
                group_dn, '(objectClass=groupOfNames)', attributes=['member']
            )
            self.assertTrue(new_dn in con.entries[0].member.value)
            self.assertTrue(user_dn not in con.entries[0].member.value)

    def test_memberof_remove_user_entry(self):
        """This test ensure `refint overlay <http://www.openldap.org/doc/
        admin24/overlays.html#Referential%20Integrity>`_ is properly set

        while moving user or removing users, make sure groups get update
        """
        with ldap_connection(
                dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
        ) as con:
            user_dn = self.assertCreateLdapUser(con, self.assertTrue)
            group_dn = self.assertCreateLdapGroup(
                con,
                self.assertTrue,
                members=[
                    user_dn,
                    'uid=tuser,ou=people,' + ROOT_DC,
                ]
            )
        with ldap_connection(dn=self.user_dn, password=self.user_pass) as con:
            self.assertTrue(con.delete(user_dn), con.result)
            con.search(
                group_dn, '(objectClass=groupOfNames)', attributes=['member']
            )
            self.assertTrue(user_dn not in con.entries[0].member.value)

    def test_change_other_people_password(self):

        def reset_password():
            with ldap_connection(
                    dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
            ) as con:
                # set password back
                self.assertTrue(
                    con.modify(
                        'uid=tuser2,ou=people,' + ROOT_DC,
                        {'userPassword': [(MODIFY_REPLACE, ['tuser2PASS'])]}
                    ),
                    con.result
                )

        self.addCleanup(reset_password)

        with ldap_connection(dn=self.user_dn, password=self.user_pass) as con:
            self.assertChangePassword(
                con,
                self.assertTrue,
                'uid=tuser2,ou=people,' + ROOT_DC,
                None,
                NEW_PASSWORD
            )


class TestRootLdapAdmin(TestLdapAdministrator):

    def setUp(self):
        super(TestRootLdapAdmin, self).setUp()
        self.user_dn = ROOT_LDAP_DN
        self.user_pass = ROOT_LDAP_SECRET

    def test_change_owns_password(self):
        # make no sense here, ignore this test for root ldap
        pass

    def test_update_own_attribute(self):
        # make no sense here, ignore this test for root ldap
        pass

    def test_edit_memberof_forbidden(self):
        # Root user can always do anything which could be useful in some
        # unexpected ways
        with ldap_connection(dn=self.user_dn, password=self.user_pass) as con:
            user_dn = self.assertCreateLdapUser(con, self.assertTrue)
            group_dn = self.assertCreateLdapGroup(con, self.assertTrue)
            self.assertTrue(
                con.modify(
                    user_dn,
                    {'memberOf': [(MODIFY_ADD, [group_dn, ])]}
                ),
                con.result
            )
            # keep it to easly test memberOf integrity config
            con.search(
                group_dn, '(objectClass=groupOfNames)', attributes=['member']
            )
            self.assertTrue(user_dn not in con.entries[0].member.value)

    def test_change_application_password(self):
        with ldap_connection(dn=self.user_dn, password=self.user_pass) as con:
            self.assertChangePassword(
                con,
                self.assertTrue,
                'uid=fakeapp,ou=applications,' + ROOT_DC,
                'fakeappPASS',
                NEW_PASSWORD
            )


class TestMemberOfRefIntIntegrity(TestCase):
    """Todo: test memberOf overlay
    http://www.openldap.org/doc/admin24/overlays.html
    #Reverse%20Group%20Membership%20Maintenance

    + TODO: make sure ldap administrator can add member and CAN NOT ADD
    memberOf, according manual test I've done integrity works only when
    adding member not the reverse entry.

    + TODO: test memberOf on a replicat: as long overlays can be configured
    differently on replicates server we should find some way to test replicat
    the day we start to use them
    """
    pass


class TestLdapConnection(TestCase):

    def get_connection(self, server_params=None, connection_params=None):
        if not server_params:
            server_params = {}
        if not connection_params:
            connection_params = {}

        serv_params = {}
        con_params = {}

        serv_params.update(server_params)
        con_params.update(connection_params)

        server = Server(LDAP_HOST, **serv_params)
        connection = Connection(server, **con_params)
        return server, connection

    def test_server_anonymous_bind(self):
        serv, connection = self.get_connection({'get_info': ALL})
        self.assertTrue(
            connection.bind(),
            "Connection error %r" % connection.result
        )
        self.assertEquals(
            ROOT_DC,
            serv.info.naming_contexts[0]
        )
        self.assertEquals(
            ['3', ],
            serv.info.supported_ldap_versions
        )
        connection.unbind()
        self.assertRaises(
            CalledProcessError,
            check_call,
            [
                "ldapsearch", "-v", "-x", "-LLL",
                "-H", LDAP_HOST,
                "ou=people," + ROOT_DC, "(objectclass=inetOrgPerson)"
                "uid", "givenName"
            ]
        )

    def test_admin_bind(self):
        check_call([
            "ldapsearch", "-v", "-x", "-LLL",
            "-H", LDAP_HOST,
            "-D", ROOT_LDAP_DN, "-w", ROOT_LDAP_SECRET, "-b",
            "uid=tadministrator,ou=people," + ROOT_DC,
            "(objectclass=inetOrgPerson)",
            "uid", "givenName"
        ])
        _, con = self.get_connection(
            connection_params={
                'user': ROOT_LDAP_DN,
                'password': ROOT_LDAP_SECRET,
            }
        )
        self.assertTrue(
            con.bind(),
            "Connection error %r" % con.result
        )
        con.unbind()
        _, con = self.get_connection(
            connection_params={
                'user': "cn=fake_username," + ROOT_DC,
                'password': ROOT_LDAP_SECRET,
            }
        )
        self.assertFalse(con.bind())
        con.unbind()
        _, con = self.get_connection(
            connection_params={
                'user': ROOT_LDAP_DN,
                'password': 'fake password',
            }
        )
        self.assertFalse(con.bind())
        con.unbind()

    def test_user(self):
        check_call([
            "ldapsearch", "-v", "-x", "-LLL",
            "-H", LDAP_HOST,
            "-D", "uid=tuser,ou=people," + ROOT_DC,
            "-w", "tuserPASS",
            "-b", "uid=tuser,ou=people," + ROOT_DC,
            "(objectclass=inetOrgPerson)", "uid", "givenName"
        ])

    def test_no_password_user(self):
        self.assertRaises(
            CalledProcessError,
            check_call,
            [
                "ldapsearch", "-v", "-x", "-LLL",
                "-H", LDAP_HOST,
                "-D", "uid=tnopassuser,ou=people," + ROOT_DC,
                "-w", "", "-b",
                "uid=tnopassuser,ou=people," + ROOT_DC,
                "(objectclass=inetOrgPerson)",
                "uid", "givenName"
            ]
        )

    def test_desactivated_user(self):
        # TODO: Define the wanted behavior and admin task
        self.assertRaises(
            CalledProcessError,
            check_call,
            [
                "ldapsearch", "-v", "-x", "-LLL",
                "-H", LDAP_HOST,
                "-D", "uid=tdisableduser,ou=people," + ROOT_DC,
                "-w", "tdisableduserPASS", "-b",
                "uid=tdisableduser,ou=people," + ROOT_DC,
                "(objectclass=inetOrgPerson)",
                "uid", "givenName"
            ]
        )
