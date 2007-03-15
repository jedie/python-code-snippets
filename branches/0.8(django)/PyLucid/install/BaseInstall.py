
"""
A base class for every _install view.
"""

from PyLucid.settings import PYLUCID_VERSION_STRING, INSTALL_PASS
from PyLucid.utils import check_pass

from django.http import HttpResponse, Http404
from django.template import Template, Context


# Warning: If debug is on, the install password is in the traceback!!!
#debug = True
debug = False

simple_render_template = """
{% extends "PyLucid/install/base.html" %}
{% block content %}
{% if headline %}<h1>{{ headline|escape }}</h1>{% endif %}
<pre>{{ output|escape }}</pre>
{% endblock %}
"""

class BaseInstall(object):
    """
    Base class for all install views.
    """
    def __init__(self, request, install_pass):
        self.request = request
        self._check_pass(install_pass)
        self.context = {
            "version": PYLUCID_VERSION_STRING,
            "install_pass": install_pass,
        }

    def _render(self, template):
        """
        Render a string-template with the given context and
        returns the result as a HttpResponse object.
        """
        c = Context(self.context)
        t = Template(template)
        html = t.render(c)
        return HttpResponse(html)

    def _simple_render(self, output, headline=None):
        """
        a simple way to render a output.
        Use simple_render_template.
        """
        self.context["output"] = "".join(output)
        if headline:
            self.context["headline"] = headline
        return self._render(simple_render_template)


    def _check_pass(self, install_pass):
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






