
"""
2. some tests
"""

import inspect, cgi, sys, time, StringIO

from PyLucid import settings
from PyLucid.utils import check_pass
from PyLucid.tools.OutBuffer import Redirector

from django.http import HttpResponse
from django.template import Template, Context, loader

from django import newforms as forms

   
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





class PythonEvalForm(forms.Form):
    """
    django newforms
    """
    codeblock = forms.CharField(
        widget=forms.widgets.Textarea(attrs={"rows":10, "style": "width: 95%;"})
    )
    object_access = forms.BooleanField(required=False)

access_deny = """
{% extends "PyLucid/install/base.html" %}
{% block content %}
<h2>Access Error:</h2>
<h3>Python Webshell is disabled.</h3>
<p>
    You must enable this features in your settings.py!
</p>
{% endblock %}
"""
python_input_form = """
{% extends "PyLucid/install/base.html" %}
{% block content %}
Execute code with Python v{{ sysversion }}:<br />

<form method="post">
    {{ PythonEvalForm }}
    <input value="execute" name="execute" type="submit">
</form>
<p>
    With access to pylucid objects you can use this objects:<br />
    <ul>{% for item in objectlist %}<li>{{ item }}</li>{% endfor %}</ul>
    Use <em>help(object)</em> for more information ;)
</p>
{% if output %}
<fieldset><legend>executed in {{ duration|stringformat:"0.3f" }}sec.:</legend>
    <pre>{{ output }}</pre>
</fieldset>
{% endif %}
<br />
{% endblock %}
"""
def evileval(request, install_pass):
    """
    4. a Python web-shell
    """
    check_pass(install_pass)
    
    if not settings.INSTALL_EVILEVAL:
        # Feature is not enabled.
        t = Template(access_deny)
        html = t.render(Context({}))
        return HttpResponse(html)
      
    if "codeblock" in request.POST:
        # Form has been sended
        init_values = request.POST.copy()
    else:
        # Requested the first time -> insert a init codeblock
        init_values = {
            "codeblock": (
                "# sample code\n"
                "for i in xrange(5):\n"
                "    print 'This is cool', i"
            ),
        }
    
    eval_form = PythonEvalForm(init_values)
    context = Context({
        "sysversion": sys.version,
        "PythonEvalForm": eval_form.as_p(),
        "objectlist": ["request"],
    })
    
    if "codeblock" in request.POST and eval_form.is_valid():
        # a codeblock was submited and the form is valid -> run the code
        codeblock = eval_form.clean_data["codeblock"]
        codeblock = codeblock.replace("\r\n", "\n") # Windows
        
        start_time = time.time()

        stderr = StringIO.StringIO()
        stdout_redirector = Redirector(stderr)
        globals = {}
        locals = {}

        try:
            code = compile(codeblock, "<stdin>", "exec", 0, 1)
            if eval_form.clean_data["object_access"]:
                exec code
            else:
                exec code in globals, locals
        except:
            import traceback
            etype, value, tb = sys.exc_info()
            tb = tb.tb_next
            msg = ''.join(traceback.format_exception(etype, value, tb))
            sys.stdout.write(msg)

        output = stdout_redirector.get()
        stderr = stderr.getvalue()
        if stderr != "":
            output += "\n---\nError:" + stderr
            
        if output == "":
            output = "[No output]"
            
        context["output"] = cgi.escape(output)

        context["duration"] = time.time() - start_time
    
    t = Template(python_input_form)
    html = t.render(context)
    return HttpResponse(html)
