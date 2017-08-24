from uuid import uuid4

from .features import LdapTestCase, ROOT_DC, ORGANIZATION


class TestLdapCreateEntries(LdapTestCase):
    def test_create_user(self):

        def create_ldap_user(con, context, data):
            user_uid = "user-%s" % uuid4()
            user_dn = 'uid=%s,ou=people,%s' % (user_uid, ROOT_DC)
            data['new_user_dn'] = user_dn
            return (
                con.add(
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
                con.result
            )

        def assert_uid_exists(con, context, data):
            self.assertEntryExists(
                data['new_user_dn'], {"cn": 'Fake User'}
            )

        def assert_uid_does_not_exists(con, context, data):
            entries = self.get_ldap_dn(data['new_user_dn'], ['cn'])
            self.assertTrue(
                len(entries) == 0
            )

        test_suite = {
            'anonymous': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_uid_does_not_exists
            },
            'user': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_uid_does_not_exists,
            },
            'user-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_uid_exists,
            },
            'user-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_uid_does_not_exists,
            },
            'user-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_uid_exists,
            },
            'admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_uid_exists,
            },
            'app': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_uid_does_not_exists,
            },
            'app-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_uid_exists,
            },
            'app-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_uid_does_not_exists,
            },
            'app-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_uid_exists,
            },
        }
        self.run_case(
            create_ldap_user,
            test_suite,
            "Test creating new user"
        )

    def test_create_group(self):

        def create_ldap_group(con, context, data):
            group_cn = "group-%s" % uuid4()
            group_dn = 'cn=%s,ou=groups,%s' % (group_cn, ROOT_DC)
            data['new_dn'] = group_dn
            return (
                con.add(
                    group_dn,
                    'groupOfNames',
                    {
                        'cn': group_cn,
                        'description': 'test group',
                        'member': ['uid=tuser,ou=people,' + ROOT_DC]
                    }
                ),
                con.result
            )

        def assert_dn_exists(con, context, data):
            self.assertEntryExists(
                data['new_dn'], {"description": 'test group'}
            )

        def assert_dn_does_not_exists(con, context, data):
            entries = self.get_ldap_dn(data['new_dn'], ['cn'])
            self.assertTrue(
                len(entries) == 0
            )

        test_suite = {
            'anonymous': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_dn_does_not_exists
            },
            'user': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_dn_does_not_exists,
            },
            'user-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_dn_exists,
            },
            'user-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_dn_does_not_exists,
            },
            'user-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_dn_exists,
            },
            'admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_dn_exists,
            },
            'app': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_dn_does_not_exists,
            },
            'app-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_dn_exists,
            },
            'app-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_dn_does_not_exists,
            },
            'app-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_dn_exists,
            },
        }
        self.run_case(
            create_ldap_group,
            test_suite,
            "Test creating new group"
        )

    def test_create_application(self):

        def create_ldap_app_user(con, context, data):
            app_uid = "user-%s" % uuid4()
            app_dn = 'uid=%s,ou=applications,%s' % (app_uid, ROOT_DC)
            data['new_user_dn'] = app_dn
            return (
                con.add(
                    app_dn,
                    'inetOrgPerson',
                    {
                        'cn': 'Fake app',
                        'sn': 'Fake',
                        'uid': app_uid,
                        'userPassword': 'Fake Pass %s' % app_uid,
                    }
                ),
                con.result
            )

        def assert_uid_exists(con, context, data):
            self.assertEntryExists(
                data['new_user_dn'], {"cn": 'Fake app'}
            )

        def assert_uid_does_not_exists(con, context, data):
            entries = self.get_ldap_dn(data['new_user_dn'], ['cn'])
            self.assertTrue(
                len(entries) == 0
            )

        test_suite = {
            'anonymous': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_uid_does_not_exists
            },
            'user': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_uid_does_not_exists,
            },
            'user-people-admin': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_uid_does_not_exists,
            },
            'user-apps-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_uid_exists,
            },
            'user-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_uid_exists,
            },
            'admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_uid_exists,
            },
            'app': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_uid_does_not_exists,
            },
            'app-people-admin': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_uid_does_not_exists,
            },
            'app-apps-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_uid_exists,
            },
            'app-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_uid_exists,
            },
        }
        self.run_case(
            create_ldap_app_user,
            test_suite,
            "Test creating new application"
        )

    def test_create_policy(self):

        def create_policy(con, context, data):
            policy_cn = "policy-%s" % uuid4()
            policy_dn = 'cn=%s,ou=policies,%s' % (policy_cn, ROOT_DC)
            data['new_dn'] = policy_dn
            return (
                con.add(
                    policy_dn,
                    ['person', 'pwdPolicy', ],
                    {
                        'cn': policy_cn,
                        'sn': 'test policy',
                        'pwdAttribute': 'userPassword',
                    }
                ),
                con.result
            )

        def assert_dn_exists(con, context, data):
            self.assertEntryExists(
                data['new_dn'], {"sn": 'test policy'}
            )

        def assert_dn_does_not_exists(con, context, data):
            entries = self.get_ldap_dn(data['new_dn'], None)
            self.assertTrue(
                len(entries) == 0
            )

        test_suite = {
            'anonymous': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_dn_does_not_exists
            },
            'user': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_dn_does_not_exists,
            },
            'user-people-admin': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_dn_does_not_exists,
            },
            'user-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_dn_does_not_exists,
            },
            'user-admin': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_dn_does_not_exists,
            },
            'admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_dn_exists,
            },
            'app': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_dn_does_not_exists,
            },
            'app-people-admin': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_dn_does_not_exists,
            },
            'app-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_dn_does_not_exists,
            },
            'app-admin': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_dn_does_not_exists,
            },
        }
        self.run_case(
            create_policy,
            test_suite,
            "Test creating new policy"
        )
