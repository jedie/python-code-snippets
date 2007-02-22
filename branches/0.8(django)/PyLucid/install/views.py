# Create your views here.

from django.http import HttpResponse
from django.db import connection

#~ from PyLucid.db import DBwrapper
import os, cgi

import sys, cgi, inspect

from django.template import Template, Context, loader

from PyLucid.models import Page


inspectdb_template = """
{% extends "PyLucid/install/base.html" %}
{% block content %}
<h1>inspectdb</h1>
<pre>
{% for line in inspectdb %}{{ line }}<br />{% endfor %}
</pre>
{% endblock %}
"""
def inspectdb(request):
    """
    django.core.management.instectdb
    """
    #~ return HttpResponse("JO")

    from django.core.management import inspectdb

    inspectdb_data = list(inspectdb())

    t = Template(inspectdb_template)
    c = Context({
        "inspectdb": inspectdb_data,
    })
    html = t.render(c)
    return HttpResponse(html)

info_template = """
{% extends "PyLucid/install/base.html" %}
{% block content %}
<h1>Info</h1>
<h2>request objects:</h2>
<ul>
{% for item in objects %}
    <li>{{ item }}</li>
{% endfor %}
</ul>

<h2>environ info:</h2>
<ul>
{% for item in environ_info %}
    <li>{{ item.0 }}: {{ item.1|escape }}</li>
{% endfor %}
</ul>
{% endblock %}
"""
def info(request, url_info):

    objects = []
    for item in dir(request):
        if not item.startswith("__"):
            objects.append("request.%s" % item)

    environ_info = []
    for key in sorted(request.environ):
        environ_info.append(
            (key,request.environ[key])
        )

    t = Template(info_template)
    c = Context({
        "objects": objects,
        "environ_info": environ_info,
    })
    html = t.render(c)
    return HttpResponse(html)

def index(request, url_info):
    response = HttpResponse()
    response.write(HTML_head)
    response.write("<h1>menu</h1>")
    response.write("<p>url: [%s]</p>" % url_info)
    response.write("<pre>")

    method_list = inspect.getmembers(Install, inspect.ismethod)
    for method_name in method_list:
        method_name = method_name[0]
        response.write(repr(
            method_name
        ))

    response.write("</pre>")
    response.write(HTML_bottom)
    return response



    response.write(cgi.escape(repr(dir(Pages))))
    response.write("\n")
    response.write(cgi.escape(repr(Pages.objects)))
    response.write("\n")
    response.write(cgi.escape(repr(Pages)))
    response.write("\n")

    for entry in Pages.objects.all():
        response.write(cgi.escape(repr(dir(entry))))
        response.write("\n")
        response.write(cgi.escape(repr(entry)))
        response.write(cgi.escape(entry.title))
        response.write("\n")

    page = Pages.objects.get(id__exact=1)
    response.write("title id=1: %s" % cgi.escape(page.title))

    old = sys.stdout
    sys.stdout = response
    help(Pages)
    sys.stdout = old



