#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid JS-SHA-Login
    ~~~~~~~~~~~~~~~~~~~~

    A secure JavaScript SHA-1 Login.

    TODO: Only plaintext login implemented!!!

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

from PyLucid.tools import crypt


DEBUG = True
#DEBUG = False
# IMPORTANT:
# Should realy only use for debugging!!!


from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.system.context_processors import add_dynamic_context

USERNAME_SESSION_KEY = "login_username"

class WrongPassword(Exception):
    pass

class auth(PyLucidBasePlugin):
    def login(self):
        if USERNAME_SESSION_KEY in self.request.session:
            # Username has been inputed in the past
            return self.input_pass()

        UsernameForm = forms.form_for_model(User, fields=("username",))

        if self.request.method == 'POST':
            username_form = UsernameForm(self.request.POST)
            if username_form.is_valid():
                username = username_form.cleaned_data["username"]
                try:
                    return self.input_pass(username)
                except User.DoesNotExist, msg:
                    self.page_msg(_("User does not exist."))
                    if DEBUG:
                        self.page_msg(msg)
        else:
            username_form = UsernameForm()

        context = {
            "fallback_url": self.URLs.adminLink(""),
            "form": username_form,
        }
        self._render_template("input_username", context)#, debug=True)


    def input_pass(self, username=None):
        if username:
            # login()
            user = User.objects.get(username = username)
            # Save username in Session:
            self.request.session[USERNAME_SESSION_KEY] = user.id
        else:
            # Username from session
            if DEBUG: self.page_msg("get user id from session.")
            user_id = self.request.session[USERNAME_SESSION_KEY]
            user = User.objects.get(id = user_id)

        self.page_msg("user:", user)

        PasswordForm = forms.form_for_model(User, fields=("password",))

        if self.request.method == 'POST':
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
            "form": password_form,
        }
        self._render_template("input_password", context)#, debug=True)


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


    def logout(self):
        logout(self.request)

        # rebuild the login/logout link:
        add_dynamic_context(self.request, self.context)

        self.page_msg.green("You logged out.")












