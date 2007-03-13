
"""
some userfull routines for the _install section
"""

from PyLucid.settings import PYLUCID_VERSION_STRING, INSTALL_PASS

from django.http import HttpResponse, Http404
from django.template import Template, Context#, loader

# Warning: If debug is on, the install password is in the traceback!!!
#debug = True
debug = False

def render(context, template):
    """
    Render a string-template with the given context and
    returns the result as a HttpResponse object.
    """
    context["version"] = PYLUCID_VERSION_STRING
    c = Context(context)
    t = Template(template)
    html = t.render(c)
    return HttpResponse(html)


def check_pass(install_pass):
    """
    Check if the _install password is right.
    raise a Http404 if the password is wrong.
    """
    password = install_pass.split("/",1)[0]

    def error(msg):
        msg = "*** install password error: %s! ***" % msg
        if debug:
            msg += " [Debug: '%s' != '%s']" % (
                password, INSTALL_PASS
            )
        raise Http404(msg)
        #~ from django.core.exceptions import ObjectDoesNotExist
        #~ raise ObjectDoesNotExist(msg)

    if password == "":
        error("no password in URL")

    if len(password)<8:
        error("password to short")

    if password != INSTALL_PASS:
        error("wrong password")