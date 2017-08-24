from ldap3 import Server, Connection, ALL
from unittest import TestCase
from subprocess import CalledProcessError, check_call

from .features import LDAP_HOST, ROOT_DC, ROOT_LDAP_DN, ROOT_LDAP_SECRET


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
            "uid=tuser,ou=people," + ROOT_DC,
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

    def test_deactivated_user(self):
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
