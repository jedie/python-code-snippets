
from django.http import Http404

from PyLucid import settings

def check_pass(install_pass):
    def error(msg):
        raise Http404("*** install password error: %s! ***" % msg)
        #~ from django.core.exceptions import ObjectDoesNotExist
        #~ raise ObjectDoesNotExist(msg)

    if install_pass == "":
        error("no password in URL")

    if len(install_pass)<8:
        error("password to short")

    if install_pass != settings.INSTALL_PASS:
        error("wrong password")