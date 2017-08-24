from uuid import uuid4

from .features import LdapTestCase, ROOT_DC


class TestLdapRemoveEntries(LdapTestCase):
    def test_remove_app_entry(self):
        def prepare_test(con, context, data):
            user_uid = "user-%s" % uuid4()
            user_dn = "uid=%s,ou=applications,%s" % (user_uid, ROOT_DC)
            self.create_app(user_uid, user_dn)
            data["dn"] = user_dn

        def delete_dn_entry(con, context, data):
            return con.delete(data['dn']), con.result

        def assert_dn_exists(con, context, data):
            self.assertEntryExists(
                data['dn'], None
            )

        def assert_dn_does_not_exists(con, context, data):
            entries = self.get_ldap_dn(data['dn'], None)
            self.assertTrue(
                len(entries) == 0
            )

        test_suite = {
            'anonymous': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists
            },
            'user': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'user-people-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'user-apps-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'user-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'app': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'app-people-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'app-apps-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'app-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
        }
        self.run_case(
            delete_dn_entry,
            test_suite,
            "Test creating delete user dn"
        )

    def test_remove_group_entry(self):

        def prepare_test(con, context, data):
            group_cn = "group-%s" % uuid4()
            group_dn = "cn=%s,ou=groups,%s" % (group_cn, ROOT_DC)
            self.create_group(
                group_cn,
                group_dn,
                members=["uid=tuser2,ou=people," + ROOT_DC]
            )
            data["dn"] = group_dn

        def delete_dn_entry(con, context, data):
            return con.delete(data['dn']), con.result

        def assert_dn_exists(con, context, data):
            self.assertEntryExists(
                data['dn'], None
            )

        def assert_dn_does_not_exists(con, context, data):
            entries = self.get_ldap_dn(data['dn'], None)
            self.assertTrue(
                len(entries) == 0
            )

        test_suite = {
            'anonymous': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists
            },
            'user': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'user-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'user-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'user-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'app': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'app-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'app-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'app-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
        }
        self.run_case(
            delete_dn_entry,
            test_suite,
            "Test creating delete user dn"
        )

    def test_remove_policy_entry(self):

        def prepare_test(con, context, data):
            policy_cn = "policy-%s" % uuid4()
            policy_dn = "cn=%s,ou=policies,%s" % (policy_cn, ROOT_DC)
            self.create_policy(policy_cn, policy_dn)
            data["dn"] = policy_dn

        def delete_dn_entry(con, context, data):
            return con.delete(data['dn']), con.result

        def assert_dn_exists(con, context, data):
            self.assertEntryExists(
                data['dn'], None
            )

        def assert_dn_does_not_exists(con, context, data):
            entries = self.get_ldap_dn(data['dn'], None)
            self.assertTrue(
                len(entries) == 0
            )

        test_suite = {
            'anonymous': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists
            },
            'user': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'user-people-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'user-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'user-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'app': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'app-people-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'app-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'app-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
        }
        self.run_case(
            delete_dn_entry,
            test_suite,
            "Test creating delete user dn"
        )

    def test_remove_user_entry(self):
        def prepare_test(con, context, data):
            user_uid = "user-%s" % uuid4()
            user_dn = "uid=%s,ou=people,%s" % (user_uid, ROOT_DC)
            self.create_user(user_uid, user_dn)
            data["dn"] = user_dn

        def delete_dn_entry(con, context, data):
            return con.delete(data['dn']), con.result

        def assert_dn_exists(con, context, data):
            self.assertEntryExists(
                data['dn'], None
            )

        def assert_dn_does_not_exists(con, context, data):
            entries = self.get_ldap_dn(data['dn'], None)
            self.assertTrue(
                len(entries) == 0
            )

        test_suite = {
            'anonymous': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists
            },
            'user': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'user-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'user-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'user-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'app': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'app-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'app-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'app-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
        }
        self.run_case(
            delete_dn_entry,
            test_suite,
            "Test creating delete user dn"
        )
