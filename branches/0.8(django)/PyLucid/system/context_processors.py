
"""
setup some "static" variables
"""

from PyLucid import settings

def static(request):
    context_extras = {}

    #___________________________________________________________________________

    context_extras['powered_by'] = (
        '<a href="http://www.pylucid.org">PyLucid v%s</a>'
    ) % settings.PYLUCID_VERSION_STRING

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
            '<a href="/_admin/logout">logout [%s]</a>'
        ) % request.user.username
    else:
        context_extras["login_link"] = '<a href="/_admin">login</a>'

    #___________________________________________________________________________

    return context_extras