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

DEBUG = True
#DEBUG = False
# IMPORTANT:
# Should realy only use for debugging!!!

from PyLucid.tools import crypt
from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.system.context_processors import add_dynamic_context
from PyLucid.models import JS_LoginData

class WrongPassword(Exception):
    pass

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
                    if "plaintext_login" in self.request.POST:
                        return self._plaintext_login(user)
                    else:
                        return self._sha_login(user)
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
        self.page_msg("password:", input_pass, db_pass)

        user = authenticate(username=user.username, password=input_pass)

        if user == None:
            raise WrongPassword("Wrong password.")
        if not user.is_active:
            raise WrongPassword("Error: Your account is disabled!")


        self.page_msg.green("Password ok.")
        login(self.request, user)

        # rebuild the login/logout link:
        add_dynamic_context(self.request, self.context)

    def _sha_login(self, user):
        self.page_msg(user)
        js_login_data = JS_LoginData.objects.get(user = user)
        self.page_msg(js_login_data)
        self.page_msg("SHA-1 - Not implemented completly, yet :(")

    def logout(self):
        logout(self.request)

        # rebuild the login/logout link:
        add_dynamic_context(self.request, self.context)

        self.page_msg.green("You logged out.")












