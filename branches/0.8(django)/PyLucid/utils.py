
from django.http import Http404

from PyLucid import settings

debug = True
#~ debug = False

def check_pass(install_pass):
    password = install_pass.split("/",1)[0]

    def error(msg):
        msg = "*** install password error: %s! ***" % msg
        if debug:
            msg += " [Debug: '%s' != '%s']" % (
                password, settings.INSTALL_PASS
            )
        raise Http404(msg)
        #~ from django.core.exceptions import ObjectDoesNotExist
        #~ raise ObjectDoesNotExist(msg)

    if password == "":
        error("no password in URL")

    if len(password)<8:
        error("password to short")

    if password != settings.INSTALL_PASS:
        error("wrong password")