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
                    {'memberof': [(MODIFY_REPLACE, [GROUP_DN])]}
                ),
                con.result
            )

        def remove_member_of():
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

        def assertMemberNotSet(con, context, data):
            con.search(
                GROUP_DN, '(objectClass=groupOfNames)', attributes=['member']
            )
            self.assertFalse(USER_DN in con.entries[0].member.value)
            remove_member_of()

        test_suite = {
            'anonymous': {'assert': self.assertFalse, },
            'user': {'assert': self.assertFalse, },
            'user-people-admin': {'assert': self.assertFalse, },
            'user-apps-admin': {'assert': self.assertFalse, },
            'user-admin': {'assert': self.assertFalse, },
            'admin': {
                'assert': self.assertTrue,  # ok it's fine if ldap admin do it
                # This is to detect if at some point it's fine to edit memberof
                # directly
                'run_after_test': assertMemberNotSet,
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

        def remove_member_of():
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

        def assertMemberNotSet(con, context, data):
            con.search(
                GROUP_DN, '(objectClass=groupOfNames)', attributes=['member']
            )
            self.assertFalse(USER_DN in con.entries[0].member.value)
            remove_member_of()

        test_suite = {
            'anonymous': {'assert': self.assertFalse, },
            'user': {'assert': self.assertFalse, },
            'user-people-admin': {'assert': self.assertFalse, },
            'user-apps-admin': {'assert': self.assertFalse, },
            'user-admin': {'assert': self.assertFalse, },
            'admin': {
                'assert': self.assertTrue,  # ok it's fine if ldap admin do it
                # This is to detect if at some point it's fine to edit memberof
                # directly
                'run_after_test': assertMemberNotSet,
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

    def test_rename_user_entry(self):
        """Test renaming an user entry make sure group get upadeted

        This test ensure `refint overlay <http://www.openldap.org/doc/
        admin24/overlays.html#Referential%20Integrity>`_ is properly set
        """
        group_cn = "group-%s" % uuid4()
        group_dn = "cn=%s,ou=groups,%s" % (group_cn, ROOT_DC)
        user1_uid = "user-%s" % uuid4()
        user1_dn = "uid=%s,ou=people,%s" % (user1_uid, ROOT_DC)
        user2_uid = "uid=user-%s" % uuid4()
        user2_dn = "%s,ou=people,%s" % (user2_uid, ROOT_DC)

        def prepare(con, context, data):
            self.create_user(user1_uid, user1_dn)
            self.create_group(group_cn, group_dn, [user1_dn, ])

        def clean():
            with ldap_connection(
                    dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
            ) as root_con:
                root_con.delete(user1_dn)
                root_con.delete(user2_dn)
                root_con.delete(group_dn)

        self.addCleanup(clean)

        def test_rename(con, context, data):
                return con.modify_dn(user1_dn, user2_uid), con.result

        def assertGroupMemeberUpdated(con, context, data):
            con.search(
                group_dn, '(objectClass=groupOfNames)', attributes=['member']
            )
            self.assertTrue(user2_dn in con.entries[0].member.value)
            self.assertTrue(user1_dn not in con.entries[0].member.value)
            clean()

        test_suite = {
            'anonymous': None,
            'user': {
                'assert': self.assertFalse,
                'run_before_test': prepare,
                'run_after_test': None,
            },
            'user-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare,
                'run_after_test': assertGroupMemeberUpdated,
            },
            'user-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare,
                'run_after_test': None,
            },
            'user-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare,
                'run_after_test': assertGroupMemeberUpdated,
            },
            'admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare,
                'run_after_test': assertGroupMemeberUpdated,
            },
            'app': {
                'assert': self.assertFalse,
                'run_before_test': prepare,
                'run_after_test': None,
            },
            'app-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare,
                'run_after_test': assertGroupMemeberUpdated,
            },
            'app-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare,
                'run_after_test': None,
            },
            'app-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare,
                'run_after_test': assertGroupMemeberUpdated,
            },
        }
        self.run_case(
            test_rename,
            test_suite,
            "testing member integrity while renaming user entry"
        )

    def test_remove_user_entry(self):
        """Test remove an user entry make sure group get upadeted
        This test ensure `refint overlay <http://www.openldap.org/doc/
        admin24/overlays.html#Referential%20Integrity>`_ is properly set

        while moving user or removing users, make sure groups get update
        """
        group_cn = "group-%s" % uuid4()
        group_dn = "cn=%s,ou=groups,%s" % (group_cn, ROOT_DC)
        user1_uid = "user-%s" % uuid4()
        user1_dn = "uid=%s,ou=people,%s" % (user1_uid, ROOT_DC)
        user2_uid = "user-%s" % uuid4()
        user2_dn = "uid=%s,ou=people,%s" % (user2_uid, ROOT_DC)

        def prepare(con, context, data):
            self.create_user(user1_uid, user1_dn)
            self.create_user(user2_uid, user2_dn)
            self.create_group(group_cn, group_dn, [user1_dn, user2_dn, ])

        def clean():
            with ldap_connection(
                    dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
            ) as root_con:
                root_con.delete(user1_dn)
                root_con.delete(user2_dn)
                root_con.delete(group_dn)

        self.addCleanup(clean)

        def test_delete_user(con, context, data):
            return con.delete(user1_dn), con.result

        def assertGroupMemeberUpdated(con, context, data):
            con.search(
                group_dn, '(objectClass=groupOfNames)',
                attributes=['member']
            )
            self.assertTrue(user1_dn not in con.entries[0].member.value)
            self.assertTrue(user2_dn in con.entries[0].member.value)
            clean()

        test_suite = {
            'anonymous': None,
            'user': {
                'assert': self.assertFalse,
                'run_before_test': prepare,
                'run_after_test': None,
            },
            'user-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare,
                'run_after_test': assertGroupMemeberUpdated,
            },
            'user-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare,
                'run_after_test': None,
            },
            'user-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare,
                'run_after_test': assertGroupMemeberUpdated,
            },
            'admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare,
                'run_after_test': assertGroupMemeberUpdated,
            },
            'app': {
                'assert': self.assertFalse,
                'run_before_test': prepare,
                'run_after_test': None,
            },
            'app-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare,
                'run_after_test': assertGroupMemeberUpdated,
            },
            'app-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare,
                'run_after_test': None,
            },
            'app-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare,
                'run_after_test': assertGroupMemeberUpdated,
            },
        }
        self.run_case(
            test_delete_user,
            test_suite,
            "testing member integrity while deleting an user entry"
        )

    def test_remove_group(self):
        group_cn = "group-%s" % uuid4()
        group_dn = "cn=%s,ou=groups,%s" % (group_cn, ROOT_DC)
        group2_cn = "group-%s" % uuid4()
        group2_dn = "cn=%s,ou=groups,%s" % (group2_cn, ROOT_DC)
        user1_uid = "user-%s" % uuid4()
        user1_dn = "uid=%s,ou=people,%s" % (user1_uid, ROOT_DC)

        def prepare(con, context, data):
            self.create_user(user1_uid, user1_dn)
            self.create_group(group_cn, group_dn, [user1_dn, ])
            self.create_group(group2_cn, group2_dn, [user1_dn, ])

        def clean():
            with ldap_connection(
                    dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
            ) as root_con:
                root_con.delete(user1_dn)
                root_con.delete(group_dn)
                root_con.delete(group2_dn)

        self.addCleanup(clean)

        def test_delete_group(con, context, data):
            return con.delete(group_dn), con.result

        def assertUserMemeberOfUpdated(con, context, data):
            con.search(
                user1_dn, '(objectClass=inetOrgPerson)',
                attributes=['memberof']
            )
            self.assertTrue(group_dn not in con.entries[0].memberof.value)
            self.assertTrue(group2_dn in con.entries[0].memberof.value)
            clean()

        test_suite = {
            'anonymous': {
                'assert': self.assertFalse,
                'run_before_test': prepare,
                'run_after_test': None,
            },
            'user': {
                'assert': self.assertFalse,
                'run_before_test': prepare,
                'run_after_test': None,
            },
            'user-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare,
                'run_after_test': assertUserMemeberOfUpdated,
            },
            'user-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare,
                'run_after_test': None,
            },
            'user-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare,
                'run_after_test': assertUserMemeberOfUpdated,
            },
            'admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare,
                'run_after_test': assertUserMemeberOfUpdated,
            },
            'app': {
                'assert': self.assertFalse,
                'run_before_test': prepare,
                'run_after_test': None,
            },
            'app-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare,
                'run_after_test': assertUserMemeberOfUpdated,
            },
            'app-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare,
                'run_after_test': None,
            },
            'app-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare,
                'run_after_test': assertUserMemeberOfUpdated,
            },
        }
        self.run_case(
            test_delete_group,
            test_suite,
            "testing member integrity while deleting an user entry"
        )
