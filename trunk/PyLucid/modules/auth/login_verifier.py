#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Abwicklung von Login/Logout


Last commit info:
----------------------------------
$LastChangedDate:$
$Rev:$
$Author: jensdiemer $

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php

"""



# =True: Login-Fehler sind aussagekräftiger: Sollte allerdings
# wirklich nur zu Debug-Zwecke eingesetzt werden!!!
#~ debug = True
debug = False

from PyLucid.system import crypt
from PyLucid.system.BaseModule import PyLucidBaseModule

from PyLucid.modules.auth.exceptions import *


from md5 import new as md5_new
def md5(txt):
    return md5_new(txt).hexdigest()



class LoginVerifier(PyLucidBaseModule):
    def __init__(self, request, response, checksum_checker):
        super(LoginVerifier, self).__init__(request, response)

        self.checksum_checker = checksum_checker

    def check_md5_login(self):
        """
        Überprüfen der md5-JavaScript-Logindaten
        - Der Username wurde schon in "Step 1" eingegeben.
            - Die MD5 Summe des Usernamens steckt in einem Cookie
            - Der md5username wird nochmal überprüft
        """
        if debug:
            self.session.debug()

        if debug:
            self.page_msg("form data:", self.request.form)
        try:
            md5_a2  = self.request.form["md5_a2"]
            md5_b  = self.request.form["md5_b"]
        except KeyError, e:
            # Formulardaten nicht vollständig
            if debug:
                self.page_msg("CGI-Keys: ", self.request.form.keys())
            msg = self._error_msg(
                "Form data not complete! KeyError: '%s'" % e,
                "LogIn form Error!"
            )
            raise PasswordError(msg)

        try:
            self.checksum_checker(md5_a2)
            self.checksum_checker(md5_b, should_len=16)
        except ValueError, e:
            msg = self._error_msg(
                "Checksum check error: %s" % e,
                "LogIn checksum check Error!"
            )
            raise PasswordError(msg)

        try:
            md5username = self.request.cookies["md5username"].value
            self.checksum_checker(md5username) # Falls falsch -> ValueError
        except (KeyError, ValueError):
            msg = self._error_msg(
                "Can't get md5username from cookie!",
                "LogIn cookie Error!"
            )
            raise PasswordError(msg)

        try:
            challenge = str(self.session["challenge"])
        except KeyError:
            msg = self._error_msg(
                "Can't get challenge from session: KeyError!",
                "LogIn session Error!"
            )
            raise PasswordError(msg)

        # Wenn wir schon die Userdaten aus der DB holen, können wir gleich
        # alle holen ;)
        select_items = ["id", "name", "md5checksum", "admin"]
        userdata = self.db.get_userdata_by_md5username(
            md5username, select_items
        )

        db_checksum = userdata["md5checksum"]

        self.check_login(db_checksum, md5_a2, md5_b, challenge)

        return userdata


    #________________________________________________________________________

    def check_login(self, db_checksum, md5_a2, md5_b, challenge):
        try:
            decrypted_checksum = crypt.decrypt(db_checksum, md5_b)
        except crypt.CryptError, e:
            msg = self._error_msg(
                "decrypt Error: %s" % e,
                "LogIn Error!"
            )
            raise PasswordError(msg)

        md5_challenge = md5(challenge + decrypted_checksum)

        if md5_challenge != md5_a2:
            msg = self._error_msg(
                "checksum Error: db_checksum: %s - cal.checksum:%s" % (
                    db_checksum, md5_challenge
                ),
                "LogIn Error!"
            )
            raise PasswordError(msg)

    #________________________________________________________________________

    def _error_msg(self, log_msg, public_msg):
        """Fehler werden abhängig vom Debug-Status angezeigt/gespeichert"""
        self.log(log_msg)

        self.session["isadmin"] = False
        self.session["user"] = False
        # Soll beim commit aktualisiert werden:
        self.session.state = "update session"

        if self.preferences["ModuleManager_error_handling"] == False:
            msg = "%s - Debug: %s" % (public_msg, log_msg)
        else:
            msg = public_msg

        return msg






