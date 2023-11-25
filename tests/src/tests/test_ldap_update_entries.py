from ldap3 import MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE
from uuid import uuid4

from .features import ldap_connection, LdapTestCase
from .features import ROOT_DC, ROOT_LDAP_SECRET, ROOT_LDAP_DN


class TestLdapUpdateEntries(LdapTestCase):

    def test_update_own_cn_attribute(self):

        def update_cn_attribute(con, context, data):
            return (
                con.modify(
                    context['user_dn'],
                    {'cn': [(MODIFY_REPLACE, ['Name change'])]}),
                con.result
            )

        def assert_name_changed(con, context, data):
            with ldap_connection(
                    dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
            ) as root_con:
                root_con.search(
                    context['user_dn'],
                    '(objectclass=inetOrgPerson)',
                    attributes=['cn']
                )
                self.assertEqual(
                    "Name change",
                    root_con.entries[0].cn.value
                )

        def assert_name_not_changed(con, context, data):
            with ldap_connection(
                    dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
            ) as root_con:
                root_con.search(
                    context['user_dn'],
                    '(objectclass=inetOrgPerson)',
                    attributes=['cn']
                )
                self.assertNotEqual(
                    "Name change",
                    root_con.entries[0].cn.value,
                    "user %s - Name shouldn't been changed" % (
                        context['user_dn'],
                    )
                )

        test_suite = {
            'anonymous': None,
            'user': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_name_not_changed
            },
            'user-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_name_changed
            },
            'user-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_name_not_changed
            },
            'user-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_name_changed
            },
            'admin': None,
            'app': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_name_not_changed
            },
            'app-people-admin': {
                'assert': self.assertFalse,
                'run_before_test': None,
                'run_after_test': assert_name_not_changed
            },
            'app-apps-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_name_changed
            },
            'app-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_name_changed
            },
        }
        self.run_case(
            update_cn_attribute,
            test_suite,
            "testing to update its own cn attribute"
        )

    def test_update_user_cn_attribute(self):
        DN = 'uid=tuser2,ou=people,' + ROOT_DC

        def update_cn_attribute(con, context, data):
            data['new_value'] = "user-%s" % uuid4()
            return (
                con.modify(
                    DN,
                    {'cn': [(MODIFY_REPLACE, [data['new_value']])]}),
                con.result
            )

        def init_old_value(con, context, data):
            with ldap_connection(
                    dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
            ) as root_con:
                root_con.search(
                    DN,
                    '(objectclass=inetOrgPerson)',
                    attributes=['cn']
                )
                data['old_value'] = root_con.entries[0].cn.value

        def assert_name_changed(con, context, data):
            with ldap_connection(
                    dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
            ) as root_con:
                root_con.search(
                    DN,
                    '(objectclass=inetOrgPerson)',
                    attributes=['cn']
                )
                self.assertEqual(
                    data['new_value'],
                    root_con.entries[0].cn.value,
                    "user %s - Name should be equal to %s" % (
                        context['user_dn'], data['new_value']
                    )
                )

        def assert_name_not_changed(con, context, data):
            with ldap_connection(
                    dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
            ) as root_con:
                root_con.search(
                    DN,
                    '(objectclass=inetOrgPerson)',
                    attributes=['cn']
                )
                self.assertEqual(
                    data['old_value'],
                    root_con.entries[0].cn.value,
                    "user %s - should not change other user "
                    "attribute" % (
                        context['user_dn'],
                    )
                )

        test_suite = {
            'anonymous': {
                'assert': self.assertFalse,
                'run_before_test': init_old_value,
                'run_after_test': assert_name_not_changed
            },
            'user': {
                'assert': self.assertFalse,
                'run_before_test': init_old_value,
                'run_after_test': assert_name_not_changed
            },
            'user-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_name_changed
            },
            'user-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': init_old_value,
                'run_after_test': assert_name_not_changed
            },
            'user-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_name_changed
            },
            'admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_name_changed
            },
            'app': {
                'assert': self.assertFalse,
                'run_before_test': init_old_value,
                'run_after_test': assert_name_not_changed
            },
            'app-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_name_changed
            },
            'app-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': init_old_value,
                'run_after_test': assert_name_not_changed
            },
            'app-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_name_changed
            },
        }
        self.run_case(
            update_cn_attribute,
            test_suite,
            "testing to update user cn attribute"
        )

    def test_update_group_description_attribute(self):

        def update_description_attribute(con, context, data):
            data['new_value'] = "blabla-%s" % uuid4()
            return (
                con.modify(
                    'cn=fakeapp,ou=groups,' + ROOT_DC,
                    {'description': [(MODIFY_REPLACE, [data['new_value']])]}),
                con.result
            )

        def init_old_value(con, context, data):
            with ldap_connection(
                    dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
            ) as root_con:
                root_con.search(
                    'cn=fakeapp,ou=groups,' + ROOT_DC,
                    '(objectclass=groupOfNames)',
                    attributes=['description']
                )
                data['old_value'] = root_con.entries[0].description.value

        def assert_description_changed(con, context, data):
            with ldap_connection(
                    dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
            ) as root_con:
                root_con.search(
                    'cn=fakeapp,ou=groups,' + ROOT_DC,
                    '(objectclass=groupOfNames)',
                    attributes=['description']
                )
                self.assertEqual(
                    data['new_value'],
                    root_con.entries[0].description.value,
                    "user %s - Description should be equal to %s" % (
                        context['user_dn'], data['new_value']
                    )
                )

        def assert_description_not_changed(con, context, data):
            with ldap_connection(
                    dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
            ) as root_con:
                root_con.search(
                    'cn=fakeapp,ou=groups,' + ROOT_DC,
                    '(objectclass=groupOfNames)',
                    attributes=['description']
                )
                self.assertEqual(
                    data['old_value'],
                    root_con.entries[0].description.value,
                    "user %s - should not change other user "
                    "attribute" % (
                        context['user_dn'],
                    )
                )

        test_suite = {
            'anonymous': {
                'assert': self.assertFalse,
                'run_before_test': init_old_value,
                'run_after_test': assert_description_not_changed
            },
            'user': {
                'assert': self.assertFalse,
                'run_before_test': init_old_value,
                'run_after_test': assert_description_not_changed
            },
            'user-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_description_changed
            },
            'user-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': init_old_value,
                'run_after_test': assert_description_not_changed
            },
            'user-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_description_changed
            },
            'admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_description_changed
            },
            'app': {
                'assert': self.assertFalse,
                'run_before_test': init_old_value,
                'run_after_test': assert_description_not_changed
            },
            'app-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_description_changed
            },
            'app-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': init_old_value,
                'run_after_test': assert_description_not_changed
            },
            'app-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_description_changed
            },
        }
        self.run_case(
            update_description_attribute,
            test_suite,
            "testing to update group description attribute"
        )

    def test_update_group_member_attribute(self):
        group_cn = "group-%s" % uuid4()
        group_dn = "cn=%s,ou=groups,%s" % (group_cn, ROOT_DC)
        user1_uid = "user-%s" % uuid4()
        user1_dn = "uid=%s,ou=people,%s" % (user1_uid, ROOT_DC)
        user2_uid = "user-%s" % uuid4()
        user2_dn = "uid=%s,ou=people,%s" % (user2_uid, ROOT_DC)
        app_uid = "app-%s" % uuid4()
        app_dn = "uid=%s,ou=applications,%s" % (app_uid, ROOT_DC)

        def clean():
            with ldap_connection(
                    dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
            ) as root_con:
                root_con.delete(group_dn)
                root_con.delete(user1_dn)
                root_con.delete(user2_dn)
                root_con.delete(app_dn)

        self.addCleanup(clean)

        def prepare(con, context, data):
            clean()
            self.create_user(user1_uid, user1_dn)
            self.create_user(user2_uid, user2_dn)
            self.create_app(app_uid, app_dn)
            self.create_group(group_cn, group_dn, [user1_dn, ])

        def define_group_members(con, context, data):
            return (
                con.modify(
                    group_dn,
                    {'member': [(MODIFY_ADD, [app_dn, user2_dn])]}),
                con.result
            )

        test_suite = {
            'anonymous': {
                'assert': self.assertFalse,
                'run_before_test': prepare,
                'run_after_test': None
            },
            'user': {
                'assert': self.assertFalse,
                'run_before_test': prepare,
                'run_after_test': None
            },
            'user-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare,
                'run_after_test': None
            },
            'user-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare,
                'run_after_test': None
            },
            'user-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare,
                'run_after_test': None
            },
            'admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare,
                'run_after_test': None
            },
            'app': {
                'assert': self.assertFalse,
                'run_before_test': prepare,
                'run_after_test': None
            },
            'app-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare,
                'run_after_test': None
            },
            'app-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': prepare,
                'run_after_test': None
            },
            'app-admin': {
                'assert': self.assertTrue,
                'run_before_test': prepare,
                'run_after_test': None
            },
        }
        self.run_case(
            define_group_members,
            test_suite,
            "testing to update group member attribute"
        )

    def test_update_access_rule(self):
        def udapte_ldap_access_rule(con, context, data):
            return con.modify(
                "olcDatabase={1}mdb,cn=config",
                {'olcAccess': [(MODIFY_ADD, [
                    '{100}to dn.subtree="ou=people,%s" '
                    'by self write' % ROOT_DC
                ])]}
            ), con.result

        test_suite = {
            'anonymous': {'assert': self.assertFalse, },
            'user': {'assert': self.assertFalse, },
            'user-people-admin': {'assert': self.assertFalse, },
            'user-apps-admin': {'assert': self.assertFalse, },
            'user-admin': {'assert': self.assertFalse, },
            'admin': {'assert': self.assertFalse, },
            'app': {'assert': self.assertFalse, },
            'app-people-admin': {'assert': self.assertFalse, },
            'app-apps-admin': {'assert': self.assertFalse, },
            'app-admin': {'assert': self.assertFalse, },
        }

        self.run_case(
            udapte_ldap_access_rule,
            test_suite,
            "testing change ldap admin password"
        )

    def test_update_app_cn_attribute(self):
        DN = 'uid=fakeapp,ou=applications,' + ROOT_DC

        def update_cn_attribute(con, context, data):
            data['new_value'] = "app-%s" % uuid4()
            return (
                con.modify(
                    DN,
                    {'cn': [(MODIFY_REPLACE, [data['new_value']])]}),
                con.result
            )

        def init_old_value(con, context, data):
            with ldap_connection(
                    dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
            ) as root_con:
                root_con.search(
                    DN,
                    '(objectclass=inetOrgPerson)',
                    attributes=['cn']
                )
                data['old_value'] = root_con.entries[0].cn.value

        def assert_name_changed(con, context, data):
            with ldap_connection(
                    dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
            ) as root_con:
                root_con.search(
                    DN,
                    '(objectclass=inetOrgPerson)',
                    attributes=['cn']
                )
                self.assertEqual(
                    data['new_value'],
                    root_con.entries[0].cn.value,
                    "user %s - Name should be equal to %s" % (
                        context['user_dn'], data['new_value']
                    )
                )

        def assert_name_not_changed(con, context, data):
            with ldap_connection(
                    dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
            ) as root_con:
                root_con.search(
                    DN,
                    '(objectclass=inetOrgPerson)',
                    attributes=['cn']
                )
                self.assertEqual(
                    data['old_value'],
                    root_con.entries[0].cn.value,
                    "user %s - should not change other user "
                    "attribute" % (
                        context['user_dn'],
                    )
                )

        test_suite = {
            'anonymous': {
                'assert': self.assertFalse,
                'run_before_test': init_old_value,
                'run_after_test': assert_name_not_changed
            },
            'user': {
                'assert': self.assertFalse,
                'run_before_test': init_old_value,
                'run_after_test': assert_name_not_changed
            },
            'user-people-admin': {
                'assert': self.assertFalse,
                'run_before_test': init_old_value,
                'run_after_test': assert_name_not_changed
            },
            'user-apps-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_name_changed
            },
            'user-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_name_changed
            },
            'admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_name_changed
            },
            'app': {
                'assert': self.assertFalse,
                'run_before_test': init_old_value,
                'run_after_test': assert_name_not_changed
            },
            'app-people-admin': {
                'assert': self.assertFalse,
                'run_before_test': init_old_value,
                'run_after_test': assert_name_not_changed
            },
            'app-apps-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_name_changed
            },
            'app-admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_name_changed
            },
        }
        self.run_case(
            update_cn_attribute,
            test_suite,
            "testing to update user cn attribute"
        )

    def test_update_policy(self):
        DN = 'cn=default,ou=policies,' + ROOT_DC

        def update_sn_attribute(con, context, data):
            data['new_value'] = "policy-%s" % uuid4()
            return (
                con.modify(
                    DN,
                    {'sn': [(MODIFY_REPLACE, [data['new_value']])]}),
                con.result
            )

        def init_old_value(con, context, data):
            with ldap_connection(
                    dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
            ) as root_con:
                root_con.search(
                    DN,
                    '(objectclass=person)',
                    attributes=['sn']
                )
                data['old_value'] = root_con.entries[0].sn.value

        def assert_name_changed(con, context, data):
            with ldap_connection(
                    dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
            ) as root_con:
                root_con.search(
                    DN,
                    '(objectclass=person)',
                    attributes=['sn']
                )
                self.assertEqual(
                    data['new_value'],
                    root_con.entries[0].sn.value,
                    "user %s - Name should be equal to %s" % (
                        context['user_dn'], data['new_value']
                    )
                )

        def assert_name_not_changed(con, context, data):
            with ldap_connection(
                    dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
            ) as root_con:
                root_con.search(
                    DN,
                    '(objectclass=person)',
                    attributes=['sn']
                )
                self.assertEqual(
                    data['old_value'],
                    root_con.entries[0].sn.value,
                    "user %s - should not change other user "
                    "attribute" % (
                        context['user_dn'],
                    )
                )

        test_suite = {
            'anonymous': {
                'assert': self.assertFalse,
                'run_before_test': init_old_value,
                'run_after_test': assert_name_not_changed
            },
            'user': {
                'assert': self.assertFalse,
                'run_before_test': init_old_value,
                'run_after_test': assert_name_not_changed
            },
            'user-people-admin': {
                'assert': self.assertFalse,
                'run_before_test': init_old_value,
                'run_after_test': assert_name_not_changed
            },
            'user-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': init_old_value,
                'run_after_test': assert_name_not_changed
            },
            'user-admin': {
                'assert': self.assertFalse,
                'run_before_test': init_old_value,
                'run_after_test': assert_name_not_changed
            },
            'admin': {
                'assert': self.assertTrue,
                'run_before_test': None,
                'run_after_test': assert_name_changed
            },
            'app': {
                'assert': self.assertFalse,
                'run_before_test': init_old_value,
                'run_after_test': assert_name_not_changed
            },
            'app-people-admin': {
                'assert': self.assertFalse,
                'run_before_test': init_old_value,
                'run_after_test': assert_name_not_changed
            },
            'app-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': init_old_value,
                'run_after_test': assert_name_not_changed
            },
            'app-admin': {
                'assert': self.assertFalse,
                'run_before_test': init_old_value,
                'run_after_test': assert_name_not_changed
            },
        }
        self.run_case(
            update_sn_attribute,
            test_suite,
            "testing to update poclicy sn attribute"
        )

    def test_update_own_password(self):

        def init_fake_password(con, context, data):
            data['password'] = 'fakepass-%s' % uuid4()

        def update_my_password(con, context, data):
            return self.change_ldap_password(
                con, context['user_dn'], context['password'], data['password'])

        def reset_password(con, context, data):
            self.reset_password(context['user_dn'], context['password'])

        def read_own_entry(con, context, data):
            self.assertTrue(
                con.search(context['user_dn'], '(objectclass=*)'),
                "User %s could not read it's own entry %r, got %r" % (
                    con.user, context['user_dn'], con.result)
            )

        def assert_update_password(con, context, data):
            with ldap_connection(
                dn=context["user_dn"],
                password=data["password"]
            ) as new_con:
                read_own_entry(new_con, context, data)
            reset_password(con, context, data)
            with ldap_connection(
                dn=context["user_dn"],
                password=context["password"]
            ) as new_con:
                read_own_entry(new_con, context, data)

        test_suite = {
            'anonymous': None,
            'user': {
                'assert': self.assertTrue,
                'run_before_test': init_fake_password,
                'run_after_test': assert_update_password,
            },
            'user-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': init_fake_password,
                'run_after_test': assert_update_password,
            },
            'user-apps-admin': {
                'assert': self.assertTrue,
                'run_before_test': init_fake_password,
                'run_after_test': assert_update_password,
            },
            'user-admin': {
                'assert': self.assertTrue,
                'run_before_test': init_fake_password,
                'run_after_test': assert_update_password,
            },
            'admin': None,
            'app': {
                'assert': self.assertFalse,
                'run_before_test': init_fake_password,
                'run_after_test': None,
            },
            'app-people-admin': {
                'assert': self.assertFalse,
                'run_before_test': init_fake_password,
                'run_after_test': None
            },
            'app-apps-admin': {
                'assert': self.assertTrue,
                'run_before_test': init_fake_password,
                'run_after_test': assert_update_password,
            },
            'app-admin': {
                'assert': self.assertTrue,
                'run_before_test': init_fake_password,
                'run_after_test': assert_update_password,
            },
        }
        self.run_case(
            update_my_password,
            test_suite,
            "Test updating its own password"
        )

    def test_update_user_password(self):
        USER_DN = "uid=tuser2,ou=people," + ROOT_DC
        POLICY_DN = "cn=testPolicy,ou=policies," + ROOT_DC

        def remove_pwdPolicySubentry():
            self.reset_password(USER_DN, 'tuser2PASS')
            with ldap_connection(
                    dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
            ) as con:
                con.modify(
                    USER_DN,
                    {
                        'pwdPolicySubentry': [(
                            MODIFY_DELETE,
                            [POLICY_DN]
                        )]
                    }
                )
                con.delete(POLICY_DN)

        # clean up pwdPolicySubentry on tuser
        self.addCleanup(remove_pwdPolicySubentry)

        # Create a dedicate policy for tuser to make test predictable
        with ldap_connection(
                dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
        ) as con:
            con.add(
                POLICY_DN,
                ['person', 'pwdPolicy', ],
                {
                    'cn': 'testPolicy',
                    'sn': 'test policy',
                    'pwdAttribute': 'userPassword',
                }
            )
            con.modify(
                USER_DN,
                {
                    'pwdPolicySubentry': [(
                        MODIFY_ADD,
                        [POLICY_DN]
                    )]
                }
            )

        def init_tuser_password(con, context, data):
            self.reset_password(USER_DN, 'tuser2PASS')
            data['new_pass'] = "test-%s" % uuid4()

        def udapte_password(con, context, data):
            return con.modify(
                USER_DN,
                {'userPassword': [(MODIFY_REPLACE, [data['new_pass']])]}
            ), con.result

        def assert_updated_password(con, context, data):
            with ldap_connection(
                dn=USER_DN,
                password=data["new_pass"]
            ) as new_con:
                self.assertTrue(new_con.search(USER_DN, '(objectclass=*)'))
            self.reset_password(USER_DN, 'tuser2PASS')

        test_suite = {
            'anonymous': {
                'assert': self.assertFalse,
                'run_before_test': init_tuser_password,
                'run_after_test': None,
            },
            'user': {
                'assert': self.assertFalse,
                'run_before_test': init_tuser_password,
                'run_after_test': None,
            },
            'user-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': init_tuser_password,
                'run_after_test': assert_updated_password,
            },
            'user-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': init_tuser_password,
                'run_after_test': None,
            },
            'user-admin': {
                'assert': self.assertTrue,
                'run_before_test': init_tuser_password,
                'run_after_test': assert_updated_password
            },
            'admin':  {
                'assert': self.assertTrue,
                'run_before_test': init_tuser_password,
                'run_after_test': assert_updated_password
            },
            'app': {
                'assert': self.assertFalse,
                'run_before_test': init_tuser_password,
                'run_after_test': None,
            },
            'app-people-admin': {
                'assert': self.assertTrue,
                'run_before_test': init_tuser_password,
                'run_after_test': assert_updated_password,
            },
            'app-apps-admin': {
                'assert': self.assertFalse,
                'run_before_test': init_tuser_password,
                'run_after_test': None,
            },
            'app-admin': {
                'assert': self.assertTrue,
                'run_before_test': init_tuser_password,
                'run_after_test': assert_updated_password,
            },
        }
        self.run_case(
            udapte_password,
            test_suite,
            "Test updating an other user password"
        )

    def test_update_root_admin_password(self):

        def udapte_ldap_admin_password(con, context, data):
            return con.modify(
                "olcDatabase={1}mdb,cn=config",
                {'olcRootPW': [(MODIFY_REPLACE, ['test'])]}
            ), con.result

        test_suite = {
            'anonymous': {'assert': self.assertFalse, },
            'user': {'assert': self.assertFalse, },
            'user-people-admin': {'assert': self.assertFalse, },
            'user-apps-admin': {'assert': self.assertFalse, },
            'user-admin': {'assert': self.assertFalse, },
            'admin': {'assert': self.assertFalse, },
            'app': {'assert': self.assertFalse, },
            'app-people-admin': {'assert': self.assertFalse, },
            'app-apps-admin': {'assert': self.assertFalse, },
            'app-admin': {'assert': self.assertFalse, },
        }

        self.run_case(
            udapte_ldap_admin_password,
            test_suite,
            "testing change ldap admin password"
        )

    def test_update_app_password(self):

        APP_DN = "uid=fakeapp,ou=applications," + ROOT_DC
        APP_PASS = 'fakeappPASS'
        POLICY_DN = "cn=testPolicy,ou=policies," + ROOT_DC

        def remove_pwdPolicySubentry():
            self.reset_password(APP_DN, APP_PASS)
            with ldap_connection(
                    dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
            ) as con:
                con.modify(
                    APP_DN,
                    {
                        'pwdPolicySubentry': [(
                            MODIFY_DELETE,
                            [POLICY_DN]
                        )]
                    }
                )
                con.delete(POLICY_DN)

        # clean up pwdPolicySubentry on tuser
        self.addCleanup(remove_pwdPolicySubentry)

        # Create a dedicate policy for tuser to make test predictable
        with ldap_connection(
                dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
        ) as con:
            con.add(
                POLICY_DN,
                ['person', 'pwdPolicy', ],
                {
                    'cn': 'testPolicy',
                    'sn': 'test policy',
                    'pwdAttribute': 'userPassword',
                }
            )
            con.modify(
                APP_DN,
                {
                    'pwdPolicySubentry': [(
                        MODIFY_ADD,
                        [POLICY_DN]
                    )]
                }
            )

        def init_fakeapp_password(con, context, data):
            self.reset_password(APP_DN, APP_PASS)
            data['new_pass'] = "test-%s" % uuid4()

        def udapte_password(con, context, data):
            return con.modify(
                APP_DN,
                {'userPassword': [(MODIFY_REPLACE, [data['new_pass']])]}
            ), con.result

        def assert_updated_password(con, context, data):
            with ldap_connection(
                dn=APP_DN,
                password=data["new_pass"]
            ) as new_con:
                self.assertTrue(new_con.search(APP_DN, '(objectclass=*)'))
            self.reset_password(APP_DN, APP_PASS)

        test_suite = {
            'anonymous': {
                'assert': self.assertFalse,
                'run_before_test': init_fakeapp_password,
                'run_after_test': None,
            },
            'user': {
                'assert': self.assertFalse,
                'run_before_test': init_fakeapp_password,
                'run_after_test': None,
            },
            'user-people-admin': {
                'assert': self.assertFalse,
                'run_before_test': init_fakeapp_password,
                'run_after_test': None,
            },
            'user-apps-admin': {
                'assert': self.assertTrue,
                'run_before_test': init_fakeapp_password,
                'run_after_test': assert_updated_password,
            },
            'user-admin': {
                'assert': self.assertTrue,
                'run_before_test': init_fakeapp_password,
                'run_after_test': assert_updated_password
            },
            'admin':  {
                'assert': self.assertTrue,
                'run_before_test': init_fakeapp_password,
                'run_after_test': assert_updated_password
            },
            'app': {
                'assert': self.assertFalse,
                'run_before_test': init_fakeapp_password,
                'run_after_test': None,
            },
            'app-people-admin': {
                'assert': self.assertFalse,
                'run_before_test': init_fakeapp_password,
                'run_after_test': None,
            },
            'app-apps-admin': {
                'assert': self.assertTrue,
                'run_before_test': init_fakeapp_password,
                'run_after_test': assert_updated_password,
            },
            'app-admin': {
                'assert': self.assertTrue,
                'run_before_test': init_fakeapp_password,
                'run_after_test': assert_updated_password,
            },
        }
        self.run_case(
            udapte_password,
            test_suite,
            "Test updating an other app password"
        )
