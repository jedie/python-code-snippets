
"""
A base class for every _install view.
"""

import sys

from PyLucid.settings import INSTALL_PASS
from PyLucid import PYLUCID_VERSION_STRING
from PyLucid.system.response import SimpleStringIO
from PyLucid.tools.crypt import make_salt_hash, check_salt_hash
from PyLucid.tools.content_processors import render_string_template

from django import newforms as forms
from django.http import HttpResponse, Http404
from django.utils.translation import ugettext as _
from django.template import Template, Context, loader
# The loader must be import, even if it is not used directly!!!
# Note: The loader makes this: add_to_builtins('django.template.loader_tags')
# In loader_tags are 'block', 'extends' and 'include' defined.


# Warning: If debug is on, the install password is in the traceback!!!
#debug = True
DEBUG = False


def check_install_password(password):
    """
    compare the given >password< with the INSTALL_PASS.
    raise a WrongPassword if the password is not the same.
    """
    def error(msg):
        msg = _("error:") + msg
        if DEBUG:
            msg += " [Debug: '%s' != '%s']" % (
                password, INSTALL_PASS
            )
        raise WrongPassword(msg)
    if INSTALL_PASS == None:
        error(_("no passwort set in your settings.py"))
    elif len(INSTALL_PASS)<8:
        error(_("The password in your settings.py is to short"))
    elif password != INSTALL_PASS:
        error(_(
            "Your old password was entered incorrectly."
            " Please enter it again."
        ))


def save_password_cookie(password):
    """
    Store the verified password as a hash in a client cookie.
    Return a HttpResponse object with cookie.
    """
    salt_hash = make_salt_hash(password)
    response = HttpResponse()
    response.set_cookie("instpass", value=salt_hash, max_age=None)
    #, expires=None, path='/', domain=None, secure=None)
    return response


def check_cookie_pass(request):
    """
    check if the _install section password is stored in the cookie
    - returns True if the password hash is ok
    - returns False if there is no password or the hash test failed
    """
    cookie_pass = request.COOKIES.get("instpass", None)
    if cookie_pass and check_salt_hash(INSTALL_PASS, cookie_pass) == True:
        # The salt-hash stored in the cookie is ok
        return True
    else:
        return False


class InstallPassForm(forms.Form):
    """ a django newforms for input the _install section password """
    password = forms.CharField(
        _('password'), min_length=8,
        help_text=_('The install password from your settings.py')
    )

LOGIN_TEMPLATE = """
{% extends "install_base.html" %}
{% block content %}
<h1>{% trans 'Log in' %}</h1>

{% if msg %}<h3>{{ msg|escape }}</h3>{% endif %}

<form method="post" action=".">
  <table class="form">
    {{ form }}
  </table>
  <input type="submit" value="{% trans 'Log in' %}" />
</form>
<p>{% trans 'Note: Cookies must be enabled.' %}</p>
{% endblock %}
"""
LOGGED_IN_TEMPLATE = """
{% extends "install_base.html" %}
{% block content %}
<h1>{% trans 'Login' %}</h1>

<p>{% trans 'Access permit. Your logged in!' %}</p>
<p><a href="{% url PyLucid.install.menu . %}">{% trans 'continue' %}</a></p>

{% endblock %}
"""

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
    def __init__(self, request):
        if INSTALL_PASS == None or len(INSTALL_PASS)<8:
            raise Http404(
                "Install password not set or too short."
                " - Install section deactivated"
            )

        self.request = request
        self.context = {
            "output": "",
            "http_host": request.META.get("HTTP_HOST","cms page"),
            "version": PYLUCID_VERSION_STRING,
        }

    #___________________________________________________________________________

    def start_view(self):
        """
        - Check the install password / login cookie
        - starts the self.view() if login ok
        - display the login form if login not ok
        """
        if check_cookie_pass(self.request) == True:
            # access ok -> start the normal _instal view() method
            return self.view()

        # The _install section password is not in the cookie
        # -> display a html input form or check a submited form

        if self.request.method == 'POST':
            # A form was submit
            form = InstallPassForm(self.request.POST)
            if form.is_valid():
                # The submited form is ok
                form_data = form.cleaned_data
                password = form_data["password"]
                try:
                    check_install_password(password)
                except WrongPassword, msg:
                    # Display the form again
                    self.context["msg"] = msg
                else:
                    # Password is ok. -> User login
                    response = save_password_cookie(password)
                    html = render_string_template(LOGGED_IN_TEMPLATE, self.context)
                    response.write(html)
                    return response
        else:
            # Create a empty form
            form = InstallPassForm()

        self.context["form"] = form.as_table()
        self.context["no_menu_link"] = True # no "back to menu" link
        return self._render(LOGIN_TEMPLATE)

    #___________________________________________________________________________

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
        render the template and returns the result as a HttpResponse object.
        """
        html = render_string_template(template, self.context)
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



class WrongPassword(Exception):
    """
    Wrong _install section password
    """
    pass






