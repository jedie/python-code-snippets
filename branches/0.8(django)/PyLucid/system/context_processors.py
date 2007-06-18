
"""
setup some "static" variables
"""

from django.utils.translation import ugettext as _

from PyLucid import PYLUCID_VERSION_STRING

def static(request):
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

    if request.user.username != "":
        # User is loged in
        context_extras["login_link"] = (
            '<a href="/_admin/logout">%s [%s]</a>'
        ) % (_("Log out"), request.user.username)
    else:
        context_extras["login_link"] = '<a href="/_admin">%s</a>' % _("Log in")

    #___________________________________________________________________________

    return context_extras
