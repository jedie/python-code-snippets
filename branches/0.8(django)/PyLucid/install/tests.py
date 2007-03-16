
"""
4. some tests
"""

from PyLucid.install.BaseInstall import BaseInstall
from PyLucid.tools.OutBuffer import Redirector

from django import newforms as forms

import cgi, sys, time, StringIO



#______________________________________________________________________________

class InspectDB(BaseInstall):
    def view(self):
        from django.core.management import inspectdb
    
        # ToDo: anders interieren und mit try-except umschliessen.
        try:
            output = "\n".join(inspectdb())
        except Exception, e:
            output = "inspect db error: %s" % e
    
        return self._simple_render(output, headline="inspectdb")

def inspectdb(request, install_pass):
    """
    1. inspect the database
    """
    return InspectDB(request, install_pass).view()
    
#______________________________________________________________________________

class SQLInfo(BaseInstall):
    def view(self):
        output = []
        
        from django.core.management import get_sql_create, get_custom_sql, get_sql_indexes
        from django.db.models import get_apps
    
        app_list = get_apps()
        
        def write_lines(lines):
            for line in lines:
                output.append("%s\n" % line)
    
        for app in app_list:
            output.append("**** sql_create:\n")
            write_lines(get_sql_create(app))
            output.append("**** get_custom_sql:\n")
            write_lines(get_custom_sql(app))
            output.append("**** get_sql_indexes:\n")
            write_lines(get_sql_indexes(app))
    
            output.append("-"*79)
            output.append("\n\n")
            
        return self._simple_render(output, headline="SQL info")
    
def sql_info(request, install_pass):
    "2. SQL info"
    return SQLInfo(request, install_pass).view()

#______________________________________________________________________________

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
class Info(BaseInstall):
    def view(self):
        from PyLucid import settings
#        from PyLucid.db import DB_Wrapper
#        import sys
#        db = DB_Wrapper(sys.stderr)#request.page_msg)
#        db_info = [
#            ("API", "%s v%s" % (db.dbapi.__name__, db.dbapi.__version__)),
#            ("Server Version", "%s (%s)" % (db.server_version, db.RAWserver_version)),
#            ("paramstyle", db.paramstyle),
#            ("placeholder", db.placeholder),
#            ("table prefix", db.tableprefix),
#        ]
    
        self.context["objects"] = []
        for item in dir(self.request):
            if not item.startswith("__"):
                self.context["objects"].append("request.%s" % item)
    
        self.context["request_meta"] = []
        for key in sorted(self.request.META):
            self.context["request_meta"].append(
                (key, self.request.META[key])
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
        self.context["current_settings"] = get_obj_infos(settings)
        
        self.context["user_info"] = get_obj_infos(self.request.user)
    
        from django.template import RequestContext
        self.context["request_context"] = RequestContext(self.request)
    
        return self._render(info_template)

def info(request, install_pass):
    """
    3. Display some information (for developers)
    """
    return Info(request, install_pass).view()


#______________________________________________________________________________

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
class URL_Info(BaseInstall):
    def view(self):
        from django.contrib.sites.models import Site
        from PyLucid.urls import urls
        
        self.context["url_info"] = urls
            
        current_site = Site.objects.get_current()
        domain = current_site.domain
        self.context["domain"] = domain

        return self._render(url_info_template)
    
def url_info(request, install_pass):
    """
    4. Display the current used urlpatterns
    """
    return URL_Info(request, install_pass).view()

#______________________________________________________________________________

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
class EvilEval(BaseInstall):
    def view(self):  
        from PyLucid.settings import INSTALL_EVILEVAL
        if not INSTALL_EVILEVAL:
            # Feature is not enabled.
            return self._render(access_deny)
    
        if "codeblock" in self.request.POST:
            # Form has been sended
            init_values = self.request.POST.copy()
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
        self.context.update({
            "sysversion": sys.version,
            "PythonEvalForm": eval_form.as_p(),
            "objectlist": ["request"],
        })
    
        if "codeblock" in self.request.POST and eval_form.is_valid():
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
                sys.stdout.write(traceback.format_exc())
    
            output = stdout_redirector.get()
            stderr = stderr.getvalue()
            if stderr != "":
                output += "\n---\nError:" + stderr
    
            if output == "":
                output = "[No output]"
    
            self.context["output"] = cgi.escape(output)
    
            self.context["duration"] = time.time() - start_time
    
        return self._render(python_input_form)

def evileval(request, install_pass):
    """
    5. a Python web-shell
    """
    return EvilEval(request, install_pass).view()


