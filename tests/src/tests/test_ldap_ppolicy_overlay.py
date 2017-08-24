from uuid import uuid4
from ldap3 import MODIFY_REPLACE

from .features import (
    LdapTestCase, ldap_connection, ROOT_LDAP_DN, ROOT_DC, ROOT_LDAP_SECRET
)


class TestLdapPPolicyOverlay(LdapTestCase):

    def test_update_own_pwdPolicySubentry(self):

        def prepare_test(con, context, data):
            policy_cn = "policy-%s" % uuid4()
            policy_dn = "cn=%s,ou=policies,%s" % (policy_cn, ROOT_DC)
            self.create_policy(policy_cn, policy_dn)
            data["dn"] = policy_dn

        def update_pwdsubpolicy_attribute(con, context, data):
            return (
                con.modify(
                    context['user_dn'],
                    {'pwdPolicySubentry': [(MODIFY_REPLACE, data['dn'])]}),
                con.result
            )

        def assert_pwdsubpolicy_changed(con, context, data):
            with ldap_connection(
                    dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
            ) as root_con:
                root_con.search(
                    context['user_dn'],
                    '(objectclass=inetOrgPerson)',
                    attributes=['pwdPolicySubentry']
                )
                self.assertEqual(
                    data['dn'],
                    root_con.entries[0].pwdPolicySubentry.value
                )

        def assert_name_not_changed(con, context, data):
            with ldap_connection(
                    dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
            ) as root_con:
                root_con.search(
                    context['user_dn'],
                    '(objectclass=inetOrgPerson)',
                    attributes=['pwdPolicySubentry']
                )
                self.assertNotEqual(
                    data['dn'],
                    root_con.entries[0].pwdPolicySubentry.value,
                    "user %s - pwdsubpolicy shouldn't been changed" % (
                        context['user_dn'],
                    )
                )

        test_suite = {
            'anonymous': None,
            'user': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_name_not_changed
            },
            'user-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_pwdsubpolicy_changed
            },
            'user-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_name_not_changed
            },
            'user-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_pwdsubpolicy_changed
            },
            'admin': None,
            'app': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_name_not_changed
            },
            'app-people-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare_test,
                'run_after_test': assert_name_not_changed
            },
            'app-apps-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_pwdsubpolicy_changed
            },
            'app-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare_test,
                'run_after_test': assert_pwdsubpolicy_changed
            },
        }
        self.run_case(
            update_pwdsubpolicy_attribute,
            test_suite,
            "testing to update its own cn attribute"
        )
