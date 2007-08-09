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

from PyLucid import models
from PyLucid.plugins_internal.auth.auth import auth
from PyLucid.models import User, JS_LoginData
from PyLucid.install.install import _create_new_superuser
from PyLucid.tools import crypt

from django.test.client import Client
from django.conf import settings


# Set the Debug mode on:
crypt.DEBUG = True


# The global test user for many testes.
# creaded in TestUserModels().test_create_new_superuser()
TEST_USERNAME = "unittest"
TEST_USER_EMAIL = "a_test@email-adress.org"
TEST_PASSWORD = "test"

# A user with a unusable password
# creaded in TestUserModels().test_unusable_password()
TEST_UNUSABLE_USER = "unitest2"



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

#    time.sleep(0.5)
#    os.remove(file_path)


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


    def test_create_new_superuser(self):
        """
        Test the create_new_superuser routine from the _install section.
        Check the User Password and JS_LoginData.
        """
        user_data = {
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD,
            "email": TEST_USER_EMAIL,
            "first_name": "", "last_name": ""
        }
        _create_new_superuser(user_data)

        self._check_userpassword(username = TEST_USERNAME)

        user = User.objects.get(username = TEST_USERNAME)
        self.failUnless(user.email == TEST_USER_EMAIL)

    def test_unusable_password(self):
        """
        if a user has a unusable password, the JS_LoginData entry must be not
        exists.
        """
        def set_and_check(user):
            "set a unusable password and check the JS_LoginData entry"
            user.set_unusable_password()
            user.save()

            try:
                JS_LoginData.objects.get(user = user)
            except JS_LoginData.DoesNotExist:
                pass
            else:
                self.fail(
                    "There should be no JS_LoginData"
                    " for a user with a unusable password"
                )

        user = User.objects.create_user(TEST_UNUSABLE_USER, '', '')
        # Set a unusable password and check:
        set_and_check(user)

        # set a password and check it.
        user.set_password('testpw')
        user.save()
        # Check if the JS_LoginData are correct.
        self._check_userpassword(username = TEST_UNUSABLE_USER)

        # set the password back to a unusable password and check:
        set_and_check(user)


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
        url_base = "/%s/1/auth/%%s/" % settings.COMMAND_URL_PREFIX
        self.login_url = url_base % "login"
        self.pass_reset_url = url_base % "pass_reset"

        self.client = Client()

    def assertStatusCode(self, response, status_code, msg=None):
        if response.status_code == status_code:
            # Page ok
            return

        debug_response(response)
        self.fail(msg)

    def assertResponse(self, response, must_contain, must_not_contain=()):
        def error(respose, msg):
            debug_response(response, msg)
            raise self.failureException, msg

        for txt in must_contain:
            if not txt in response.content:
                error(response, "Text not in response: '%s'" % txt)

        for txt in must_not_contain:
            if txt in response.content:
                error(response, "Text should not be in response: '%s'" % txt)

    #__________________________________________________________________________

    def test_django_login(self):
        # Request a django admin panel login
        response = self.client.get("/%s/" % settings.ADMIN_URL_PREFIX)
        self.assertStatusCode(response, 200)

        # login into the django admin panel
        response = self.client.post(
            "/%s/" % settings.ADMIN_URL_PREFIX,
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
        self.assertResponse(response, must_contain=("User does not exist.",))

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
            must_contain=(
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
            must_contain=(
                "Wrong password.",
                "PyLucid unsecure plaintext LogIn - step 2",
                "Password:",
                "Request a password reset.",
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
            must_contain=(
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
            must_contain=(
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
#        debug_response(response)
        self.assertStatusCode(response, 200)
        self.assertResponse(response,
            must_contain=(
                "step 2", "Log in", "Form data is not valid. Please correct."
            ),
            must_not_contain=("Request a password reset.",),
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
        self.assertResponse(response,
            must_contain=("Log in", "Form data is not valid. Please correct."),
            must_not_contain=("Request a password reset.",),

        )
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
        self.assertResponse(response,
            must_contain=("Log in", "Session Error."),
            must_not_contain=("Request a password reset.",),
        )
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
        self.assertResponse(response,
            must_contain=(
                "Log in", "Wrong password.", "Request a password reset."
            )
        )
#        debug_response(response)

    def test_SHA_login(self):
        """
        Test a SHA login with a correct password.
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
            must_contain=(
                "Password ok.",
                "Log out [%s]" % TEST_USERNAME
            )
        )

    def test_pass_reset_form1(self):
        """
        Check if we get the password reset form.
        """
        response = self.client.get(self.pass_reset_url)
#        debug_response(response)
        self.assertResponse(response, must_contain=("Reset your password:",))


    def test_pass_reset_form2(self):
        """
        Check if we get the password reset form, after we send a SHA-Login
        for a user with a unusable password.
        """
        response = self.client.post(
            self.login_url,
            {
                "username": TEST_UNUSABLE_USER,
                "sha_login" : True
            }
        )
#        debug_response(response)
        self.assertResponse(response,
            must_contain=(
                "The JS-SHA-Login data doesn't exist.",
                "You must reset your password.",
                "Reset your password:",
                TEST_UNUSABLE_USER,
            )
        )

    def test_pass_reset_form3(self):
        """
        Check if we get the password reset form, after we send a plain text
        Login for a user with a unusable password.
        """
        response = self.client.post(
            self.login_url,
            {
                "username": TEST_UNUSABLE_USER,
                "plaintext_login" : True
            }
        )
#        debug_response(response)
        self.assertResponse(response,
            must_contain=(
                "No usable password was saved.",
                "You must reset your password.",
                "Reset your password:",
                TEST_UNUSABLE_USER,
            )
        )


    def test_pass_reset_form_errors1(self):
        """
        form validating test: Check with no username and no email.
        """
        response = self.client.post(self.pass_reset_url)
        self.assertResponse(
            response, must_contain=("Form data is not valid. Please correct.",)
        )


    def test_pass_reset_form_errors2(self):
        """
        form validating test: Check with not existing user.
        """
        response = self.client.post(self.pass_reset_url,
            {"username": "wrong_user"}
        )
        self.assertResponse(response, must_contain=("User does not exist.",))


    def test_pass_reset_form_errors3(self):
        """
        form validating test: Check with valid, but wrong email adress.
        """
        response = self.client.post(self.pass_reset_url,
            {
                "username": TEST_USERNAME,
                "email": "wrong@email-adress.org"
            }
        )
        self.assertResponse(response,
            must_contain=("Wrong email address. Please correct.",)
        )


    def test_pass_reset(self):
        """
        form validating test: Check with wrong email adress.
        """
        response = self.client.post(self.pass_reset_url,
            {
                "username": TEST_USERNAME,
                "email": TEST_USER_EMAIL
            }
        )
        debug_response(response)
#        self.assertResponse(response, must_contain=("User does not exist.",))


def suite():
    # Check if the middlewares are on. Otherwise every unitest failed ;)
    middlewares = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
    )
    for m in middlewares:
        if not m in settings.MIDDLEWARE_CLASSES:
            raise EnvironmentError, "Middleware class '%s' not installed!" % m

    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(TestCryptModul))
    suite.addTest(unittest.makeSuite(TestUserModels))
    suite.addTest(unittest.makeSuite(TestSHA1Login))
    return suite

if __name__ == "__main__":
    print
    print ">>> Unitest"
    print "_"*79
    runner = unittest.TextTestRunner()
    runner.run(suite())
