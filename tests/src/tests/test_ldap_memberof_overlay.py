from ldap3 import MODIFY_REPLACE, MODIFY_DELETE
from uuid import uuid4

from .features import ldap_connection, LdapTestCase
from .features import ROOT_DC, ROOT_LDAP_SECRET, ROOT_LDAP_DN


class TestLdapMemberOfOverlay(LdapTestCase):

    def test_update_app_memberof_attribute(self):
        # Editing memberof attrs should be forbiden as long `refint overlay
        # <http://www.openldap.org/doc/admin24/
        # overlays.html#Referential%20Integrity>`_ currently is not able to
        # add member attributes on the corresponding groups (not sure if it's
        # a wrong setting or overlay limitation). As long overlay can be
        # configured differently per replicate I guess this is an overlay
        # implementation choice... Anyway at the moment we make sure we do not
        # change memberOf attribute directly
        GROUP_DN = 'cn=fakeapp,ou=groups,' + ROOT_DC
        USER_DN = 'uid=fakeapp,ou=applications,' + ROOT_DC

        def update_memberof_attribute(con, context, data):
            data['new_value'] = "app-%s" % uuid4()
            return (
                con.modify(
                    USER_DN,
                    {'memberof': [(MODIFY_REPLACE, [GROUP_DN])]}),
                con.result
            )

        def remove_member_of(con, context, data):
            with ldap_connection(
                    dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
            ) as con:
                con.modify(
                    USER_DN,
                    {
                        'memberof': [(
                            MODIFY_DELETE,
                            [GROUP_DN]
                        )]
                    }
                )

        test_suite = {
            'anonymous': {'assert': self.assertFalse, },
            'user': {'assert': self.assertFalse, },
            'user-people-admin': {'assert': self.assertFalse, },
            'user-apps-admin': {'assert': self.assertFalse, },
            'user-admin': {'assert': self.assertFalse, },
            'admin': {
                'assert': self.assertTrue,  # ok it's fine if ldap admin do it
                'run_after_test': remove_member_of,
            },
            'app': {'assert': self.assertFalse, },
            'app-people-admin': {'assert': self.assertFalse, },
            'app-apps-admin': {'assert': self.assertFalse, },
            'app-admin': {'assert': self.assertFalse, },
        }

        self.run_case(
            update_memberof_attribute,
            test_suite,
            "testing to update user cn attribute"
        )

    def test_update_people_memberof_attribute(self):
        # Editing memberof attrs should be forbiden as long `refint overlay
        # <http://www.openldap.org/doc/admin24/
        # overlays.html#Referential%20Integrity>`_ currently is not able to
        # add member attributes on the corresponding groups (not sure if it's
        # a wrong setting or overlay limitation). As long overlay can be
        # configured differently per replicate I guess this is an overlay
        # implementation choice... Anyway at the moment we make sure we do not
        # change memberOf attribute directly
        GROUP_DN = 'cn=fakeapp,ou=groups,' + ROOT_DC
        USER_DN = 'uid=tuser2,ou=people,' + ROOT_DC

        def update_memberof_attribute(con, context, data):
            data['new_value'] = "app-%s" % uuid4()
            return (
                con.modify(
                    USER_DN,
                    {'memberof': [(MODIFY_REPLACE, [GROUP_DN])]}),
                con.result
            )

        def remove_member_of(con, context, data):
            with ldap_connection(
                    dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
            ) as con:
                con.modify(
                    USER_DN,
                    {
                        'memberof': [(
                            MODIFY_DELETE,
                            [GROUP_DN]
                        )]
                    }
                )

        test_suite = {
            'anonymous': {'assert': self.assertFalse, },
            'user': {'assert': self.assertFalse, },
            'user-people-admin': {'assert': self.assertFalse, },
            'user-apps-admin': {'assert': self.assertFalse, },
            'user-admin': {'assert': self.assertFalse, },
            'admin': {
                'assert': self.assertTrue,  # ok it's fine if ldap admin do it
                'run_after_test': remove_member_of,
            },
            'app': {'assert': self.assertFalse, },
            'app-people-admin': {'assert': self.assertFalse, },
            'app-apps-admin': {'assert': self.assertFalse, },
            'app-admin': {'assert': self.assertFalse, },
        }

        self.run_case(
            update_memberof_attribute,
            test_suite,
            "testing to update user cn attribute"
        )

    def test_member_integrity(self):
        """Todo: test memberOf overlay
        http://www.openldap.org/doc/admin24/overlays.html
        #Reverse%20Group%20Membership%20Maintenance

        + TODO: make sure ldap administrator can add member and CAN NOT ADD
        memberOf, according manual test I've done integrity works only when
        adding member not the reverse entry.

        + TODO: test memberOf on a replicat: as long overlays can be configured
        differently on replicates server we should find some way to test
        replicat the day we start to use them
        """
        group_cn = "group-%s" % uuid4()
        group_dn = "cn=%s,ou=groups,%s" % (group_cn, ROOT_DC)
        group2_cn = "group-%s" % uuid4()
        group2_dn = "cn=%s,ou=groups,%s" % (group2_cn, ROOT_DC)
        user1_uid = "user-%s" % uuid4()
        user1_dn = "uid=%s,ou=people,%s" % (user1_uid, ROOT_DC)
        user2_uid = "user-%s" % uuid4()
        user2_dn = "uid=%s,ou=people,%s" % (user2_uid, ROOT_DC)
        app_uid = "app-%s" % uuid4()
        app_dn = "uid=%s,ou=applications,%s" % (app_uid, ROOT_DC)

        def prepare():
            self.create_user(user1_uid, user1_dn)
            self.create_user(user2_uid, user2_dn)
            self.create_app(app_uid, app_dn)
            self.create_group(group_cn, group_dn, [user1_dn, ])
            self.create_group(group2_cn, group2_dn, [app_dn, ])

        def clean():
            with ldap_connection(
                    dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
            ) as root_con:
                root_con.delete(group2_dn)
                root_con.delete(group_dn)
                root_con.delete(app_dn)
                root_con.delete(user1_dn)
                root_con.delete(user2_dn)

        self.fail()

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
