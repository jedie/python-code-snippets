
from PyLucid.settings import PYLUCID_VERSION_STRING

from django.http import HttpResponse
from django.template import Template, Context#, loader

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