
"""
2. some tests
"""

import inspect, cgi

from PyLucid.utils import check_pass
from PyLucid import settings

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
def inspectdb(request, install_pass):
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
<ul>
    <li><a href="#db_info">db info</a></li>
    <li><a href="#settings">settings</a></li>
    <li><a href="#user_info">user info</a></li>
    <li><a href="#request">request objects</a></li>
    <li><a href="#request_meta">request.META</a></li>
    <li><a href="#request_context">request context</a></li>
</ul>
<a name="db_info"></a>
<h2>db info</h2>
<dl>
{% for item in db_info %}
  <dt>{{ item.0 }}</dt>
  <dd>{{ item.1 }}</dd>
{% endfor %}
</dl>

<a name="settings"></a>
<a href="#top">&#x5E; top</a>
<h2>current settings</h2>
<dl>
{% for item in current_settings %}
  <dt>{{ item.0 }}</dt>
  <dd><pre>{{ item.1|pprint }}</pre></dd>
{% endfor %}
</dl>

<a name="user_info"></a>
<a href="#top">&#x5E; top</a>
<h2>user info (request.user)</h2>
<dl>
{% for item in user_info %}
  <dt>{{ item.0 }}</dt>
  <dd><pre>{{ item.1|pprint }}</pre></dd>
{% endfor %}
</dl>

<a name="request"></a>
<a href="#top">&#x5E; top</a>
<h2>request objects:</h2>
<ul>
{% for item in objects %}
    <li>{{ item }}</li>
{% endfor %}
</ul>

<a name="request_meta"></a>
<a href="#top">&#x5E; top</a>
<h2>request meta:</h2>
<ul>
{% for item in request_meta %}
    <li>{{ item.0 }}: {{ item.1|escape }}</li>
{% endfor %}
</ul>

<a name="request_context"></a>
<a href="#top">&#x5E; top</a>
<h2>request context:</h2>
<p><pre>{{ request_context|pprint }}</pre></p>

{% endblock %}
"""
def info(request, install_pass):
    """
    2. Display some information (for developers)
    """
    check_pass(install_pass)

    from PyLucid.db import DB_Wrapper
    import sys
    db = DB_Wrapper(sys.stderr)#request.page_msg)
    db_info = [
        ("API", "%s v%s" % (db.dbapi.__name__, db.dbapi.__version__)),
        ("Server Version", "%s (%s)" % (db.server_version, db.RAWserver_version)),
        ("paramstyle", db.paramstyle),
        ("placeholder", db.placeholder),
        ("table prefix", db.tableprefix),
    ]

    objects = []
    for item in dir(request):
        if not item.startswith("__"):
            objects.append("request.%s" % item)

    request_meta = []
    for key in sorted(request.META):
        request_meta.append(
            (key, request.META[key])
        )

    def get_obj_infos(obj):
        info = []
        for obj_name in dir(obj):
            if obj_name.startswith("_"):
                continue

            try:
                current_obj = getattr(obj, obj_name)
            except Exception, e:
                etype = sys.exc_info()[0]
                info.append((obj_name, "[%s: %s]" % (etype, cgi.escape(str(e)))))
                continue

            if not isinstance(current_obj, (basestring, int, tuple, bool, dict)):
                #~ print ">>>Skip:", obj_name, type(current_obj)
                continue
            info.append((obj_name, current_obj))
        info.sort()
        return info

    current_settings = get_obj_infos(settings)
    user_info = get_obj_infos(request.user)
    #~ print request.user.is_superuser

    from django.template import RequestContext
    request_context = RequestContext(request)

    t = Template(info_template)
    c = Context({
        "db_info": db_info,
        "current_settings": current_settings,
        "user_info": user_info,
        "objects": objects,
        "request_meta": request_meta,
        "request_context": request_context
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
def url_info(request, install_pass):
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