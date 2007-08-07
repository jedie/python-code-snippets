#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid JS-SHA-Login
    ~~~~~~~~~~~~~~~~~~~~

    A secure JavaScript SHA-1 Login.

    TODO: Only plaintext login implemented!!!

    TODO: Clearing the session table?
    http://www.djangoproject.com/documentation/sessions/#clearing-the-session-table

    Last commit info:
    ~~~~~~~~~
    LastChangedDate: $LastChangedDate$
    Revision.......: $Rev$
    Author.........: $Author$

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE for more details
"""

__version__ = "$Rev$"

from django import newforms as forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

#DEBUG = True
DEBUG = False
# IMPORTANT:
# Should realy only use for debugging!!!

from PyLucid import settings
from PyLucid.tools import crypt
from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.system.context_processors import add_dynamic_context
from PyLucid.models import JS_LoginData

class WrongPassword(Exception):
    pass

class SHA_LoginForm(forms.Form):
    sha_a2 = forms.CharField(
        min_length=crypt.HASH_LEN, max_length=crypt.HASH_LEN
    )
    sha_b = forms.CharField(
        min_length=crypt.HASH_LEN/2, max_length=crypt.HASH_LEN/2
    )



class auth(PyLucidBasePlugin):
    def login(self):
        UsernameForm = forms.form_for_model(User, fields=("username",))

        if self.request.method == 'POST':
            if DEBUG: self.page_msg(self.request.POST)
            username_form = UsernameForm(self.request.POST)
            if username_form.is_valid():
                username = username_form.cleaned_data["username"]
                try:
                    user = User.objects.get(username = username)
                except User.DoesNotExist, msg:
                    self.page_msg(_("User does not exist."))
                    if DEBUG:
                        self.page_msg(msg)
                else:
                    if not user.is_active:
                        raise WrongPassword("Error: Your account is disabled!")

                    if "plaintext_login" in self.request.POST:
                        return self._plaintext_login(user)
                    elif "sha_login" in self.request.POST:
                        return self._sha_login(user)
                    else:
                        self.page_msg.red("Wrong POST data.")
            else:
                if DEBUG: self.page_msg("username_form is not valid.")
        else:
            username_form = UsernameForm()

        context = {
            "fallback_url": self.URLs.adminLink(""),
            "form": username_form,
        }
        self._render_template("input_username", context)#, debug=True)

    def _plaintext_login(self, user):
        PasswordForm = forms.form_for_model(User, fields=("password",))

        # Delete the default django help text:
        PasswordForm.base_fields['password'].help_text = ""

        if self.request.method == 'POST' and "password" in self.request.POST:
            password_form = PasswordForm(self.request.POST)
            if password_form.is_valid():
                password = password_form.cleaned_data["password"]
                try:
                    self._check_plaintext_password(password, user)
                except WrongPassword, msg:
                    self.page_msg.red(msg)
                else:
                    # Login ok
                    return
        else:
            password_form = PasswordForm()

        context = {
            "username": user.username,
            "logout_url": self.URLs.methodLink("logout"),
            "form": password_form,
        }
        self._render_template("plaintext_login", context)#, debug=True)

    def _check_plaintext_password(self, input_pass, user):
        db_pass = user.password
        if DEBUG:
            self.page_msg("password:", input_pass, db_pass)

        user = authenticate(username=user.username, password=input_pass)

        if user == None:
            raise WrongPassword("Wrong password.")

        self._login_user(user)


    def _login_user(self, user):
        """
        Log the >user< in.
        Used in self._check_plaintext_password() and self._sha_login()
        """
        self.page_msg.green(_("Password ok."))
        login(self.request, user)

        # rebuild the login/logout link:
        add_dynamic_context(self.request, self.context)


    def _sha_login(self, user):
        """
        Login with the JS-SHA1-Login procedure.
        """
        js_login_data = JS_LoginData.objects.get(user = user)
        salt = js_login_data.salt

        if "sha_a2" in self.request.POST and "sha_b" in self.request.POST:
            SHA_login_form = SHA_LoginForm(self.request.POST)
            if SHA_login_form.is_valid():
                sha_a2 = SHA_login_form.cleaned_data["sha_a2"]
                sha_b = SHA_login_form.cleaned_data["sha_b"]
                if DEBUG:
                    self.page_msg("sha_a2:", sha_a2)
                    self.page_msg("sha_b:", sha_b)

                try:
                    int(sha_a2, 16)
                    int(sha_b, 16)
                except (ValueError, OverflowError), e:
                    self.page_msg.red(_("Wrong data."))
                    return

                # A submited SHA1-JS-Login form
                try:
                    challenge = self.request.session['challenge']
                    if DEBUG: self.page_msg("challenge:", challenge)
                except KeyError, e:
                    msg = _("Session Error.")
                    if DEBUG: msg = "%s (%s)" % (msg, e)
                    self.page_msg.red(msg)
                    return

                sha_checksum = js_login_data.sha_checksum
                if DEBUG: self.page_msg("sha_checksum:", sha_checksum)

                # authenticate with:
                # PyLucid.plugins_internal.auth.auth_backend.JS_SHA_Backend
                msg = _("Wrong password.")
                try:
                    user = authenticate(
                        user=user, challenge=challenge,
                        sha_a2=sha_a2, sha_b=sha_b,
                        sha_checksum=sha_checksum
                    )
                except Exception, e:
                    if DEBUG:
                        msg += " (%s)" % e
                else:
                    if user:
                        self._login_user(user)
                        return
                self.page_msg.red(msg)
            else:
                self.page_msg.red(_("Data are not valid"))


        if DEBUG:
            challenge = "debug"
        else:
            # Create a new random salt value for the password challenge:
            challenge = crypt.get_new_salt()

        # For later checking
        self.request.session['challenge'] = challenge

        PasswordForm = forms.form_for_model(User, fields=("password",))

        if self.request.method == 'POST':
            if DEBUG: self.page_msg(self.request.POST)
            password_form = PasswordForm(self.request.POST)
            if password_form.is_valid():
                password = password_form.cleaned_data["password"]
                self.page_msg("password:", password)
                self.page_msg("SHA-1 - Not implemented completly, yet :(")
                return
        else:
            password_form = PasswordForm()


        context = {
            "username": user.username,
            "fallback_url": self.URLs.adminLink(""),
            "form": password_form,
            "salt": salt,
            "challenge": challenge,
            "PyLucid_media_url": settings.PYLUCID_MEDIA_URL,
        }
        if DEBUG == True:
            # For JavaScript debug
            context["debug"] = "true"
        else:
            context["debug"] = "false"

        self._render_template("input_password", context)#, debug=True)


    def logout(self):
        logout(self.request)

        # rebuild the login/logout link:
        add_dynamic_context(self.request, self.context)

        self.page_msg.green("You logged out.")












