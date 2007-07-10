
"""
setup some "static" variables
"""

from django.utils.translation import ugettext as _

from PyLucid import PYLUCID_VERSION_STRING
from PyLucid import settings

def static(request):
    """
    A django TEMPLATE_CONTEXT_PROCESSORS
    http://www.djangoproject.com/documentation/templates_python/#writing-your-own-context-processors
    """
    context_extras = {}

    #___________________________________________________________________________

    context_extras['powered_by'] = (
        '<a href="http://www.pylucid.org">PyLucid v%s</a>'
    ) % PYLUCID_VERSION_STRING

    #___________________________________________________________________________

    # The module_manager set "must_login":
    if getattr(request, "must_login", False):
        context_extras["robots"] = "NONE,NOARCHIVE"
    else:
        context_extras["robots"] = "index,follow"

    #___________________________________________________________________________

    return context_extras



def add_dynamic_context(request, context):
    """
    Add some dynamic stuff into the context.
    """
    URLs = context["URLs"]

    #___________________________________________________________________________

    if request.user.username != "":
        # User is loged in
        url = URLs.commandLink("auth", "logout")
        txt = "%s [%s]" % (_("Log out"), request.user.username)
    else:
        url = URLs.commandLink("auth", "login")
        txt = _("Log in")

    context["login_link"] = '<a href="%s">%s</a>' % (url, txt)


