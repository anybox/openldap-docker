import os

from contextlib import contextmanager
from ldap3 import Server, Connection, ALL, MODIFY_ADD, MODIFY_REPLACE
from ldap3.extend.standard.modifyPassword import ModifyPassword
from unittest import TestCase


LDAP_HOST = os.getenv("LDAP_HOST", 'ldaps://ldap.ci.example.com')
ROOT_DC = os.getenv("ROOT_DC", "dc=ci,dc=example,dc=com")
ROOT_LDAP_SECRET = os.getenv("ROOT_LDAP_SECRET", "secret")
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


class LdapTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.users = {
            'anonymous': {
                # used for error log message
                'description': "Anonymous user, should'nt able to do anything",
                'user_dn': '',
                'password': ''
            },
            'user': {
                'description': "Authentificated user, should be able to "
                               "only read its own entry",
                'user_dn': 'uid=tuser,ou=people,' + ROOT_DC,
                'password': 'tuserPASS',
            },
            'user-people-admin': {
                'description': "Authentificated user admin, should be able to "
                               "edit people and groups (not apps)",
                'user_dn': 'uid=tadmin-people,ou=people,' + ROOT_DC,
                'password': 'tadmin-peoplePASS',
            },
            'user-apps-admin': {
                'description': "Authentificated user admin, should be able to "
                               "edit applications (not people/groups)",
                'user_dn': 'uid=tadmin-apps,ou=people,' + ROOT_DC,
                'password': 'tadmin-appsPASS',
            },
            'user-admin': {
                'description': "Authentificated user admin, should be able to "
                               "administrate people/groups/applications",
                'user_dn': 'uid=test_default_admin,ou=people,' + ROOT_DC,
                'password': 'test password',
            },
            'admin': {
                'description': "Root LDAP admin",
                'user_dn': ROOT_LDAP_DN,
                'password': ROOT_LDAP_SECRET,
            },
            'app': {
                'description': "Authentificated service, should be able read"
                               "people/groups",
                'user_dn': 'uid=fakeapp2,ou=applications,' + ROOT_DC,
                'password': 'fakeapp2PASS',
            },
            'app-people-admin': {
                'description': "Authentificated app admin, should be able to "
                               "edit people and groups (not apps)",
                'user_dn': 'uid=tapp-people-admin,ou=applications,' + ROOT_DC,
                'password': 'tapp-people-adminPASS',
            },
            'app-apps-admin': {
                'description': "Authentificated app admin, should be able to "
                               "edit applications (not people/groups)",
                'user_dn': 'uid=tapp-apps-admin,ou=applications,' + ROOT_DC,
                'password': 'tapp-apps-adminPASS',
            },
            'app-admin': {
                'description': "Authentificated app admin, should be able to "
                               "edit applications (not people/groups)",
                'user_dn': 'uid=tapp-admin,ou=applications,' + ROOT_DC,
                'password': 'tapp-adminPASS',
            },
        }

        with ldap_connection(
                dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
        ) as root_con:
            root_con.modify(
                'cn=ldap_people_admin,ou=groups,' + ROOT_DC,
                {'member': [(MODIFY_ADD, [
                    cls.users['user-people-admin']['user_dn'],
                    # already managed throught 00_organization.ldif
                    # cls.users['user-admin']['user_dn'],
                    cls.users['app-people-admin']['user_dn'],
                    cls.users['app-admin']['user_dn'],
                ])]}
            )
            root_con.modify(
                'cn=ldap_apps_admin,ou=groups,' + ROOT_DC,
                {'member': [(MODIFY_ADD, [
                    cls.users['user-apps-admin']['user_dn'],
                    # already managed throught 00_organization.ldif
                    # cls.users['user-admin']['user_dn'],
                    cls.users['app-apps-admin']['user_dn'],
                    cls.users['app-admin']['user_dn'],
                ])]}
            )

    def run_case(self, test, test_suite, error_msg):

        for user_code, infos in self.users.items():
            data = test_suite[user_code]
            if not data:
                continue
            with ldap_connection(
                dn=infos["user_dn"],
                password=infos["password"]
            ) as con:
                if 'run_before_test' in data and data['run_before_test']:
                    data['run_before_test'](con, infos, data)
                result, obj = test(con, infos, data)
                data['assert'](
                    result,
                    "Error while: %s\n"
                    "With user: %s \n"
                    "User description: %s\n"
                    "Object: %r" % (
                        error_msg, user_code, infos['description'], obj
                    )
                )
                if 'run_after_test' in data and data['run_after_test']:
                    data['run_after_test'](con, infos, data)

    def assertEntryExists(self, dn, expected_attributes=None):
        if not expected_attributes:
            expected_attributes = {}
        entries = self.get_ldap_dn(dn, expected_attributes.keys())
        self.assertTrue(
            entries
        )
        for key, value in expected_attributes.items():
            self.assertEqual(
                value,
                getattr(entries[0], key)
            )

    @staticmethod
    def change_ldap_password(
        con, user_dn, old_pass, new_pass
    ):
        ModifyPassword(
            con, user=user_dn,  old_password=old_pass, new_password=new_pass
        ).send()
        return (
            con.result['description'] == "success",
            con.result
        )

    @staticmethod
    def reset_password(dn, password):
        with ldap_connection(
                dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
        ) as con:
            assert con.modify(
                dn,
                {'userPassword': [(MODIFY_REPLACE, [password])]}
            ), con.result

    @staticmethod
    def get_ldap_dn(
        dn, attributes, ldap_filter='(objectclass=*)'
    ):
        with ldap_connection(
                dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
        ) as root_con:
            root_con.search(
                dn,
                ldap_filter,
                attributes=attributes
            )
            return root_con.entries

    @staticmethod
    def create_group(cn, dn, members):

        with ldap_connection(
                dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
        ) as root_con:
            root_con.add(
                dn,
                'groupOfNames',
                {
                    'cn': cn,
                    'description': 'test group',
                    'member': members
                }
            )

    @staticmethod
    def create_policy(cn, dn):
        with ldap_connection(
                dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
        ) as root_con:
            root_con.add(
                dn,
                ['person', 'pwdPolicy', ],
                {
                    'cn': cn,
                    'sn': 'test policy',
                    'pwdAttribute': 'userPassword',
                }
            )

    @staticmethod
    def create_user(user_uid, dn):
        with ldap_connection(
                dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
        ) as root_con:
            root_con.add(
                dn,
                'inetOrgPerson',
                {
                    'cn': 'Fake User %s' % user_uid,
                    'sn': 'Fake',
                    'mobile': 1111,
                    'givenName': 'User',
                    'o': ORGANIZATION,
                    'uid': user_uid,
                }
            )

    @staticmethod
    def create_app(app_uid, dn):
        with ldap_connection(
                dn=ROOT_LDAP_DN, password=ROOT_LDAP_SECRET
        ) as root_con:
            root_con.add(
                dn,
                'inetOrgPerson',
                {
                    'cn': 'Fake app %s' % app_uid,
                    'sn': 'Fake',
                    'uid': app_uid,
                }
            )
