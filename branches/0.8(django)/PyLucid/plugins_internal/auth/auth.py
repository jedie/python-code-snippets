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

import datetime

from django import newforms as forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


# DEBUG is usefull for debugging password reset. It send no email, it puts the
# email text direclty into the CMS page.
DEBUG = True
#DEBUG = False
# IMPORTANT:
# Should realy only use for debugging!!!
if DEBUG:
    import warnings
    warnings.warn("Debugmode is on", UserWarning)


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

    def _check_sha(self, key_name):
        if not key_name in self.cleaned_data:
            raise forms.ValidationError(u"No '%s' data in the form." % key_name)

        # Should we better use this:
        # http://www.python-forum.de/post-74578.html#74578

        sha_value = self.cleaned_data[key_name]
        try:
            int(sha_value, 16)
        except (ValueError, OverflowError), e:
            raise forms.ValidationError(u"Wrong '%s' data." % key_name)

        return sha_value

    def clean_sha_a2(self):
        """
        Validates that sha_a2 can be a valid SHA1 value.
        """
        return self._check_sha("sha_a2")

    def clean_sha_b(self):
        """
        Validates that sha_a2 can be a valid SHA1 value.
        """
        return self._check_sha("sha_b")




class auth(PyLucidBasePlugin):
    def login(self):
        if DEBUG:
            self.page_msg.red(
                "Warning: DEBUG is ON! Should realy only use for debugging!"
            )

        UsernameForm = forms.form_for_model(User, fields=("username",))
        username_form = UsernameForm(self.request.POST)

        def get_data(form):
            if self.request.method != 'POST':
                return

            if DEBUG: self.page_msg(self.request.POST)

            if not form.is_valid():
                self.page_msg.red("Form data is not valid. Please correct.")
                if DEBUG: self.page_msg(form.errors)
                return

            username = form.cleaned_data["username"]
            try:
                user = User.objects.get(username = username)
            except User.DoesNotExist, e:
                msg = _("User does not exist.")
                if DEBUG: msg += " %s" % e
                self.page_msg.red(msg)
                return

            if not user.is_active:
                self.page_msg.red(_("Error: Your account is disabled!"))
                return

            return user


        user = get_data(username_form)
        if user != None: # A valid form with a existing user was send.
            if "plaintext_login" in self.request.POST:
                return self._plaintext_login(user)
            elif "sha_login" in self.request.POST:
                return self._sha_login(user)
            else:
                self.page_msg.red("Wrong POST data.")


        context = {
            "fallback_url": self.URLs.adminLink(""),
            "form": username_form,
        }
        self._render_template("input_username", context)#, debug=True)

    def _insert_reset_link(self, context):
        """
        insert the link to the method self.pass_reset()
        used in self._plaintext_login() and self._sha_login()
        """
        context["pass_reset_link"] = self.URLs.methodLink("pass_reset")

    def _plaintext_login(self, user):
        if not user.has_usable_password():
            msg = _("No usable password was saved.")
            self.pass_reset(user.username, msg) # Display the pass reset form
            return

        PasswordForm = forms.form_for_model(User, fields=("password",))

        # Change the default TextInput to a PasswordInput
        PasswordForm.base_fields['password'].widget = forms.PasswordInput()

        context = {
            "username": user.username,
            "logout_url": self.URLs.methodLink("logout"),
        }

        # Delete the default django help text:
        PasswordForm.base_fields['password'].help_text = ""
        password_form = PasswordForm(self.request.POST)

        if "password" in self.request.POST:
            if password_form.is_valid():
                password = password_form.cleaned_data["password"]
                try:
                    self._check_plaintext_password(password, user)
                except WrongPassword, msg:
                    self.page_msg.red(msg)
                    self._insert_reset_link(context)
                else:
                    # Login ok
                    return

        context["form"] = password_form
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
        try:
            js_login_data = JS_LoginData.objects.get(user = user)
        except JS_LoginData.DoesNotExist, e:
            msg = _(
                "The JS-SHA-Login data doesn't exist."

            )
            if DEBUG:
                msg += " %s" % e
            self.pass_reset(user.username, msg) # Display the pass reset form
            return

        salt = js_login_data.salt
        context = {
            "username": user.username,
            "fallback_url": self.URLs.adminLink(""),
            "salt": salt,
            "PyLucid_media_url": settings.PYLUCID_MEDIA_URL,
        }

        if "sha_a2" in self.request.POST and "sha_b" in self.request.POST:
            SHA_login_form = SHA_LoginForm(self.request.POST)
            if not SHA_login_form.is_valid():
                self.page_msg.red("Form data is not valid. Please correct.")
                if DEBUG: self.page_msg(SHA_login_form.errors)
            else:
                sha_a2 = SHA_login_form.cleaned_data["sha_a2"]
                sha_b = SHA_login_form.cleaned_data["sha_b"]
                if DEBUG:
                    self.page_msg("sha_a2:", sha_a2)
                    self.page_msg("sha_b:", sha_b)

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
                self._insert_reset_link(context)
                self.page_msg.red(msg)


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

        context["form"] = password_form
        context["challenge"] = challenge

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

    #__________________________________________________________________________
    # Password reset

    def pass_reset(self, username=None, msg=None):
        """
        Input username and email for a password reset.
        """
        if msg:
            # Plaintext or SHA1 Login and the user has a unuseable password.
            self.page_msg.red(msg)
            self.page_msg.green(_("You must reset your password."))

        ResetForm = forms.form_for_model(User, fields=("username", "email"))
        reset_form = ResetForm(self.request.POST)

        def get_data(form):
            if not form.is_valid():
                self.page_msg.red("Form data is not valid. Please correct.")
                if DEBUG: self.page_msg(reset_form.errors)
                return

            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]

            try:
                user = User.objects.get(username = username)
            except User.DoesNotExist, e:
                msg = _("User does not exist.")
                if DEBUG: msg += " %s" % e
                self.page_msg.red(msg)
                return

            if not "@" in user.email:
                self.page_msg.red(
                    _("Can't reset password. User has no email address.")
                )
                return

            if not email == user.email:
                self.page_msg.red(
                    _("Wrong email address. Please correct.")
                )
                return

            return user


        if self.request.method == 'POST' and username==None:
            if DEBUG: self.page_msg(self.request.POST)

            user = get_data(reset_form)
            if user != None: # A valid form was sended in the past
                self._send_reset_mail(user)
                return

        context = {
            "submited": False,
            "url": self.URLs.methodLink("pass_reset"),
            "form": reset_form,
        }
        self._render_template("pass_reset_form", context)#, debug=True)

    def _send_reset_mail(self, user):
        """
        Send a mail to the user with a password reset link.
        """
        seed = crypt.get_new_seed()
        self.request.session['pass_reset_ID'] = seed
        self.page_msg("TODO:", seed)


        from django.contrib.sessions.models import Session
        session_cookie_name = settings.SESSION_COOKIE_NAME
        current_session_id = self.request.COOKIES[session_cookie_name]
        s = Session.objects.get(pk=current_session_id)
        expiry_date = s.expire_date

        expiry_time = settings.SESSION_COOKIE_AGE

        reset_link = self.URLs.methodLink("new_password", args=(seed,))

        # FIXME: convert to users local time.
        now = datetime.datetime.now()

        email_context = {
            "request_time": now,
            "base_url": self.URLs["hostname"],
            "reset_link": reset_link,
            "expiry_date": expiry_date,
            "ip": self.request.META['REMOTE_ADDR']
        }
        emailtext = self._get_rendered_template(
            "pass_reset_email", email_context,
#            debug=True
        )

        if DEBUG:
            self.page_msg("Debug! No Email was sended!")
            self.response.write("<fieldset><legend>The email text:</legend>")
            self.response.write("<pre>")
            self.response.write(emailtext)
            self.response.write("</pre></fieldset>")
        else:
            from django.core.mail import send_mail
            # TODO
#            send_mail('Subject here', 'Here is the message.', 'from@example.com',
#                ['to@example.com'], fail_silently=False)

        context = {
            "submited": True,
            "expiry_date": expiry_date,
            "expiry_time": expiry_time,
            "expire_at_browser_close": settings.SESSION_EXPIRE_AT_BROWSER_CLOSE,
        }
        self._render_template("pass_reset_form", context)#, debug=True)

    def new_password(self):
        self.page_msg("TODO: set a new password!")



