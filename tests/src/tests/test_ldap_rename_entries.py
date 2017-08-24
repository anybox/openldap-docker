from uuid import uuid4

from .features import LdapTestCase, ROOT_DC


class TestLdapRenameEntries(LdapTestCase):
    def test_rename_user_entry(self):
        def prepare_test(con, context, data):
            user_uid = "user-%s" % uuid4()
            user_dn = "uid=%s,ou=people,%s" % (user_uid, ROOT_DC)
            user2_uid = "uid=user-%s" % uuid4()
            user2_dn = "%s,ou=people,%s" % (user2_uid, ROOT_DC)
            self.create_user(user_uid, user_dn)
            data["dn"] = user_dn
            data["new_uid"] = user2_uid
            data["new_dn"] = user2_dn

        def rename_dn_entry(con, context, data):
            return con.modify_dn(data['dn'], data['new_uid']), con.result

        def assert_dn_exists(con, context, data):
            self.assertEntryExists(
                data['new_dn'], None
            )

        def assert_dn_does_not_exists(con, context, data):
            entries = self.get_ldap_dn(data['new_dn'], None)
            self.assertTrue(
                len(entries) == 0
            )

        test_suite = {
            'anonymous': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists
            },
            'user': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'user-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'user-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'user-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'app': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'app-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'app-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'app-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
        }
        self.run_case(
            rename_dn_entry,
            test_suite,
            "Test creating rename user dn"
        )

    def test_rename_app_entry(self):
        def prepare_test(con, context, data):
            app_uid = "app-%s" % uuid4()
            app_dn = "uid=%s,ou=applications,%s" % (app_uid, ROOT_DC)
            app2_uid = "uid=app-%s" % uuid4()
            app2_dn = "%s,ou=applications,%s" % (
                app2_uid, ROOT_DC
            )
            self.create_app(app_uid, app_dn)
            data["dn"] = app_dn
            data["new_uid"] = app2_uid
            data["new_dn"] = app2_dn

        def rename_dn_entry(con, context, data):
            return con.modify_dn(data['dn'], data['new_uid']), con.result

        def assert_dn_exists(con, context, data):
            self.assertEntryExists(
                data['new_dn'], None
            )

        def assert_dn_does_not_exists(con, context, data):
            entries = self.get_ldap_dn(data['new_dn'], None)
            self.assertTrue(
                len(entries) == 0
            )

        test_suite = {
            'anonymous': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists
            },
            'user': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'user-people-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'user-apps-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'user-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'app': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'app-people-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'app-apps-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'app-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
        }
        self.run_case(
            rename_dn_entry,
            test_suite,
            "Test creating rename app dn"
        )

    def test_rename_group_entry(self):

        def prepare_test(con, context, data):
            group_cn = "group-%s" % uuid4()
            group_dn = "cn=%s,ou=groups,%s" % (group_cn, ROOT_DC)
            group2_cn = "cn=group-%s" % uuid4()
            group2_dn = "%s,ou=groups,%s" % (group2_cn, ROOT_DC)
            self.create_group(
                group_cn, group_dn, ["uid=tuser,ou=people,%s" % ROOT_DC]
            )
            data["dn"] = group_dn
            data["new_cn"] = group2_cn
            data["new_dn"] = group2_dn

        def rename_dn_entry(con, context, data):
            return con.modify_dn(data['dn'], data['new_cn']), con.result

        def assert_dn_exists(con, context, data):
            self.assertEntryExists(
                data['new_dn'], None
            )

        def assert_dn_does_not_exists(con, context, data):
            entries = self.get_ldap_dn(data['new_dn'], None)
            self.assertTrue(
                len(entries) == 0
            )

        test_suite = {
            'anonymous': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists
            },
            'user': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'user-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'user-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'user-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'app': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'app-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'app-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'app-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
        }
        self.run_case(
            rename_dn_entry,
            test_suite,
            "Test creating rename group dn"
        )

    def test_rename_policy_entry(self):

        def prepare_test(con, context, data):
            policy_cn = "policy-%s" % uuid4()
            policy_dn = "cn=%s,ou=policies,%s" % (policy_cn, ROOT_DC)
            policy2_cn = "cn=policy-%s" % uuid4()
            policy2_dn = "%s,ou=policies,%s" % (policy2_cn, ROOT_DC)
            self.create_policy(policy_cn, policy_dn)
            data["dn"] = policy_dn
            data["new_cn"] = policy2_cn
            data["new_dn"] = policy2_dn

        def rename_dn_entry(con, context, data):
            return con.modify_dn(data['dn'], data['new_cn']), con.result

        def assert_dn_exists(con, context, data):
            self.assertEntryExists(
                data['new_dn'], None
            )

        def assert_dn_does_not_exists(con, context, data):
            entries = self.get_ldap_dn(data['new_dn'], None)
            self.assertTrue(
                len(entries) == 0
            )

        test_suite = {
            'anonymous': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists
            },
            'user': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'user-people-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists
            },
            'user-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'user-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists
            },
            'admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_exists,
            },
            'app': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'app-people-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists
            },
            'app-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists,
            },
            'app-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_dn_does_not_exists
            },
        }
        self.run_case(
            rename_dn_entry,
            test_suite,
            "Test creating rename policy dn"
        )
