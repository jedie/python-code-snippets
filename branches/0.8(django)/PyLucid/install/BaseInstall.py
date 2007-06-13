
"""
A base class for every _install view.
"""

import sys

from PyLucid.settings import INSTALL_PASS
from PyLucid import PYLUCID_VERSION_STRING
from PyLucid.system.response import SimpleStringIO

from django.http import HttpResponse, Http404
from django.template import Template, Context, loader
# The loader must be import, even if it is not used directly!!!
# Note: The loader makes this: add_to_builtins('django.template.loader_tags')
# In loader_tags are 'block', 'extends' and 'include' defined.


# Warning: If debug is on, the install password is in the traceback!!!
#debug = True
DEBUG = False

SIMPLE_RENDER_TEMPLATE = """
{% extends "install_base.html" %}
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
            "output": "",
            "http_host": request.META.get("HTTP_HOST","cms page"),
            "version": PYLUCID_VERSION_STRING,
            "install_pass": install_pass,
        }

    def _redirect_execute(self, method, *args, **kwargs):
        """
        run a method an redirect stdout writes (print) into a Buffer.
        puts the redirected outputs into self.context["output"].
        usefull to run django management functions.
        """
        redirect = SimpleStringIO()
        old_stdout = sys.stdout
        sys.stdout = redirect
        old_stderr = sys.stderr
        sys.stderr = redirect
        try:
            method(*args, **kwargs)
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        self.context["output"] += redirect.getvalue()

    def _render(self, template):
        """
        Render a string-template with the given context and
        returns the result as a HttpResponse object.
        """
        c = Context(self.context)
        t = Template(template)
        html = t.render(c)
        return HttpResponse(html)

    def _simple_render(self, output=None, headline=None):
        """
        a simple way to render a output.
        Use simple_render_template.
        """
        if output:
            self.context["output"] += "".join(output)
        if headline:
            self.context["headline"] = headline
        return self._render(SIMPLE_RENDER_TEMPLATE)


    def _check_pass(self, install_pass):
        """
        Check if the _install password is right.
        raise a Http404 if the password is wrong.
        """
        password = install_pass.split("/", 1)[0]

        def error(msg):
            msg = "*** install password error: %s! ***" % msg
            if DEBUG:
                msg += " [Debug: '%s' != '%s']" % (
                    password, INSTALL_PASS
                )
            raise Http404(msg)

        if password == "":
            error("no password in URL")

        if len(password)<8:
            error("password to short")

        if password != INSTALL_PASS:
            error("wrong password")






