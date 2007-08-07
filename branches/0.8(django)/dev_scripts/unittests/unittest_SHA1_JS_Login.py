#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Test the PyLucid SHA1-JS-Login

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by the PyLucid team.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from setup_environment import setup, make_insert_dump
setup(
    path_info=False, extra_verbose=False,
    syncdb=True, insert_dump=True,
    install_plugins=True
)

#______________________________________________________________________________
# Test:

import unittest, sys, re, tempfile, os, webbrowser, traceback, time

from django.test.client import Client

from PyLucid import models
from PyLucid.plugins_internal.auth.auth import auth
from PyLucid.settings import COMMAND_URL_PREFIX, ADMIN_URL_PREFIX
from PyLucid.models import User, JS_LoginData
from PyLucid.install.install import _create_new_superuser
from PyLucid.tools import crypt


# Set the Debug mode on:
crypt.DEBUG = True


TEST_USERNAME = "unittest"
TEST_PASSWORD = "test"


def create_test_user():
    print "Create test User..."
    user_data = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD,
        "first_name": "", "last_name": ""
    }
    _create_new_superuser(user_data)
    print "OK"


# Bug with Firefox under Ubuntu.
# http://www.python-forum.de/topic-11568.html
webbrowser._tryorder.insert(0, 'epiphany') # Use Epiphany, if installed.


def debug_response(response, msg=""):
    """
    Display the response content in a webbrowser.
    """
    content = response.content
    
    stack = traceback.format_stack(limit=3)[:-1]
    stack.append(msg)
    stack_info = "".join(stack)
    info = (
        "\n<br /><hr />\n"
        "<strong><pre>%s</pre></strong>\n"
        "</body>"
    ) % stack_info

    content = content.replace("</body>", info)
    
    
    fd, file_path = tempfile.mkstemp(prefix="PyLucid_unittest_", suffix=".html")
    os.write(fd, content)
    os.close(fd)
    url = "file://%s" % file_path
    print "\nDEBUG html page in Browser! (url: %s)" % url
    webbrowser.open(url)

    time.sleep(0.5)
    os.remove(file_path)


regex = re.compile(r"(\w+)\s*=\s*['\"]*([^'\"]+)['\"]*;")

def _get_JS_data(content):
    """
    retuned the JS variable statements from the given html page content.
    """
    return dict(regex.findall(content))


def _build_sha_data(JS_data, password):
    """
    Simulate the JS Routines to build the SHA1 login data from the given
    plaintext password.
    """
    salt = JS_data["salt"]
    challenge = JS_data["challenge"]

    password_hash = crypt.make_hash(password, salt)

#    print "password:", password
#    print "salt:", salt
#    print "challenge:", challenge
#    print "password_hash:", password_hash

    # Split the SHA1-Hash in two pieces
    sha_a = password_hash[:(crypt.HASH_LEN/2)]
    sha_b = password_hash[(crypt.HASH_LEN/2):]

    sha_a2 = crypt.make_hash(sha_a, challenge)

    return sha_a2, sha_b



class TestCryptModul(unittest.TestCase):
    """
    The the PyLucid.tools.crypt modul
    """
    def test_hash_function(self):
        """
        Check if crypt.make_hash() build the same hash as the routine in:
        django.contrib.auth.models.User.set_password()
        """
        raw_password = "a raw password"
        u = User.objects.create_user('hashtestuser', '', raw_password)
        u.save()

        django_password = u.password
        type, django_salt, django_hash = django_password.split("$")
        assert type == "sha1"

        password_hash = crypt.make_hash(raw_password, django_salt)

        assert django_hash == password_hash, (
            "django_hash: %s\n"
            "password_hash: %s"
        ) % (django_hash, password_hash)



class TestUserModels(unittest.TestCase):
    """
    Test the JS_LoginData
    """

    def _get_LoginData(self, username):
        user = User.objects.get(username = username)
        js_login_data = JS_LoginData.objects.get(user = user)

        return user, js_login_data

    def _check_userpassword(self, username):
        """
        Get the userdata from the database and check the creaded JS_LoginData.
        """
        user, js_login_data = self._get_LoginData(username)

        sha_checksum, salt = crypt.django_to_sha_checksum(user.password)
        assert salt == js_login_data.salt
        assert js_login_data.sha_checksum == sha_checksum, (
            "sha_checksum wrong:\n"
            " -django user table:\n"
            "    Username: '%(user)s',\n"
            "    password: '%(pass)s'\n"
            " -JS_LoginData table:\n"
            "    sha_checksum: '%(checksum1)s'\n"
            "    salt: '%(salt)s'\n"
            " -generated data:\n"
            "    sha_checksum: '%(checksum2)s'\n"
        ) % {
            "user": user.username,
            "pass": user.password,
            "checksum1": js_login_data.sha_checksum,
            "salt": js_login_data.salt,
            "checksum2": sha_checksum,
            "salt2": salt,
        }

    def test_user_model1(self):
        """
        Create a django user with the interface given from the django user
        manager and check the JS_LoginData.
        http://www.djangoproject.com/documentation/authentication/#id1
        """
        u = User.objects.create_user('testuser', '', 'testpw')
        u.save()

        self._check_userpassword(username = "testuser")


    def test_user_model2(self):
        """
        Check the User Password and JS_LoginData for the test user created in
        def create_test_user() - the _install routine to create a first user.
        (see above)
        """
        self._check_userpassword(username = TEST_USERNAME)


    def test_login(self):
        username = TEST_USERNAME

        user, js_login_data = self._get_LoginData(username)

        sha_checksum = js_login_data.sha_checksum
        salt = js_login_data.salt

        challenge = "test_challenge"
        JS_data = {
            "salt": salt,
            "challenge": challenge,
        }

        sha_a2, sha_b = _build_sha_data(JS_data, TEST_PASSWORD)

        try:
            check = crypt.check_js_sha_checksum(
                challenge, sha_a2, sha_b, sha_checksum
            )
        except Exception, e:
            msg = (
                "check_js_sha_checksum error: %s\n"
                "    user: %s\n"
                " - JS Data:\n"
                "    sha_checksum: %s\n"
                "    salt: %s\n"
                "    challenge: %s\n"
                " - _build_sha_data():\n"
                "    sha_a2: %s\n"
                "    sha_b: %s\n"
            ) % (
                e, username, sha_checksum, salt, challenge, sha_a2, sha_b
            )
            self.fail(msg)




class TestSHA1Login(unittest.TestCase):

    _open = []

    def setUp(self):
        self.login_url = '/%s/1/auth/login/' % COMMAND_URL_PREFIX
        self.client = Client()

    def assertStatusCode(self, response, status_code, msg=None):
        if response.status_code == status_code:
            # Page ok
            return

        debug_response(response)
        self.fail(msg)

    def assertResponse(self, response, text_list):
        make_debug = True
        for txt in text_list:
            if not txt in response.content:
                msg = "Text not in response: '%s'" % txt
                if make_debug:
                    debug_response(response, msg)
                make_debug = False

                raise self.failureException, msg

    #__________________________________________________________________________

    def test_django_login(self):
        # Request a django admin panel login
        response = self.client.get("/%s/" % ADMIN_URL_PREFIX)
        self.assertStatusCode(response, 200)

        # login into the django admin panel
        response = self.client.post(
            "/%s/" % ADMIN_URL_PREFIX,
            {
                "username": TEST_USERNAME,
                "password": TEST_PASSWORD,
            }
        )
        self.assertStatusCode(response, 200)

    def test_username_input(self):
        response = self.client.get(self.login_url)
        self.assertStatusCode(response, 200)

    def test_send_wrong_username(self):
        response = self.client.post(
            self.login_url, {"username": "not exists"}
        )
        self.assertStatusCode(response, 200)
        self.assertResponse(response, text_list=("User does not exist.",))

    #__________________________________________________________________________

    def test_send_username(self):
        response = self.client.post(
            self.login_url,
            {
                "username": TEST_USERNAME,
                "plaintext_login" : True
            }
        )
        self.assertStatusCode(response, 200)
        self.assertResponse(response,
            text_list=(
                "PyLucid unsecure plaintext LogIn - step 2",
                "Password:"
            )
        )

    def test_plaintext_login_wrong(self):
        response = self.client.post(
            self.login_url,
            {
                "username": TEST_USERNAME,
                "password": "a-wrong-password",
                "plaintext_login" : True
            }
        )
        self.assertStatusCode(response, 200)
        self.assertResponse(response,
            text_list=(
                "Wrong password.",
                "PyLucid unsecure plaintext LogIn - step 2",
                "Password:"
            )
        )

    def test_plaintext_login(self):
        response = self.client.post(
            self.login_url,
            {
                "username": TEST_USERNAME,
                "password": TEST_PASSWORD,
                "plaintext_login" : True
            }
        )
        self.assertStatusCode(response, 200)
        self.assertResponse(response,
            text_list=(
                "Password ok.",
                "Log out [%s]" % TEST_USERNAME
            )
        )

    #__________________________________________________________________________

    def test_send_username2(self):
        response = self.client.post(
            self.login_url,
            {
                "username": TEST_USERNAME,
                "sha_login" : True
            }
        )
        self.assertStatusCode(response, 200)
        self.assertResponse(response,
            text_list=(
                "step 2",
                "Log in"
            )
        )

    def test_SHA_wrong1(self):
        response = self.client.post(
            self.login_url,
            {
                "username": TEST_USERNAME,
                "sha_a2": "wrong", "sha_b": "wrong",
                "sha_login" : True
            }
        )
        self.assertStatusCode(response, 200)
        self.assertResponse(response,
            text_list=(
                "step 2",
                "Log in",
                "Data are not valid"
            )
        )

    def test_SHA_wrong2(self):
        """
        right length of sha_a2 and sha_b, but int(sha, 16) failed.
        """
        response = self.client.post(
            self.login_url,
            {
                "username": TEST_USERNAME,
                "sha_a2": "x234567890123456789012345678901234567890",
                "sha_b": "x2345678901234567890",
                "sha_login" : True
            }
        )
        self.assertStatusCode(response, 200)
        self.assertResponse(response, text_list=("Log in", "Wrong data."))
#        debug_response(response)

    def test_SHA_wrong3(self):
        """
        No Session.
        """
        response = self.client.post(
            self.login_url,
            {
                "username": TEST_USERNAME,
                "sha_a2": "1234567890123456789012345678901234567890",
                "sha_b": "12345678901234567890",
                "sha_login" : True
            }
        )
        self.assertStatusCode(response, 200)
        self.assertResponse(response, text_list=("Log in", "Session Error."))
#        debug_response(response)

    def test_SHA_wrong4(self):
        """
        Wrong Password
        """
        # Make a session.
        self.test_send_username2()

        response = self.client.post(
            self.login_url,
            {
                "username": TEST_USERNAME,
                "sha_a2": "1234567890123456789012345678901234567890",
                "sha_b": "12345678901234567890",
                "sha_login" : True
            }
        )
        self.assertStatusCode(response, 200)
        self.assertResponse(response, text_list=("Log in", "Wrong password."))
#        debug_response(response)

    def test_SHA_login(self):
        """
        Wrong Password
        """
        # Make a session.
        response = self.client.post(
            self.login_url,
            {
                "username": TEST_USERNAME,
                "sha_login" : True
            }
        )

        JS_data = _get_JS_data(response.content)
        sha_a2, sha_b = _build_sha_data(JS_data, TEST_PASSWORD)

        response = self.client.post(
            self.login_url,
            {
                "username": TEST_USERNAME,
                "sha_a2": sha_a2,
                "sha_b": sha_b,
                "sha_login" : True
            }
        )
#        debug_response(response)
        self.assertStatusCode(response, 200)
        self.assertResponse(response,
            text_list=(
                "Password ok.",
                "Log out [%s]" % TEST_USERNAME
            )
        )


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCryptModul))
    suite.addTest(unittest.makeSuite(TestUserModels))
    suite.addTest(unittest.makeSuite(TestSHA1Login))
    return suite

if __name__ == "__main__":
    create_test_user()
    print
    print ">>> Unitest"
    print "_"*79
    runner = unittest.TextTestRunner()
    runner.run(suite())
    #unittest.main()
    #sys.exit()