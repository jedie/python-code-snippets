
"""
2. some tests
"""

from PyLucid.utils import check_pass

from django.http import HttpResponse
from django.template import Template, Context, loader


inspectdb_template = """
{% extends "PyLucid/install/base.html" %}
{% block content %}
<h1>inspectdb</h1>
<pre>
{% for line in inspectdb %}{{ line }}<br />{% endfor %}
</pre>
{% endblock %}
"""
def inspectdb(request, install_pass, path_info=None):
    """
    1. inspect the database
    """
    check_pass(install_pass)
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
def info(request, install_pass, url_info):
    """
    2. Display some information (for developers)
    """
    check_pass(install_pass)
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

url_info_template = """
{% extends "PyLucid/install/base.html" %}
{% block content %}
<h1>URL Info for '{{ domain }}':</h1>
<table>
{% for item in url_info %}
    <tr>
        <td>{{ item.0|escape }}</td>
        <td>{{ item.1|escape }}</td>
    </tr>
{% endfor %}
</table>
{% endblock %}
"""
from django.contrib.sites.models import Site
def url_info(request, install_pass, url_info):
    """
    3. Display the current used urlpatterns
    """
    check_pass(install_pass)
    from PyLucid.urls import urls

    current_site = Site.objects.get_current()
    domain = current_site.domain

    t = Template(url_info_template)
    c = Context({
        "domain": domain,
        "url_info": urls,
    })
    html = t.render(c)
    return HttpResponse(html)