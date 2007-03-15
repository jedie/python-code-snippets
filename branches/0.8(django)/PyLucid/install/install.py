
"""
1. install

sollte ich mir mal ansehen:
http://code.djangoproject.com/wiki/CookBookScriptsMiniFlush
"""

from PyLucid import settings
from PyLucid.install.BaseInstall import BaseInstall
from PyLucid.settings import TABLE_PREFIX
from PyLucid.system.response import PyLucidResponse
from PyLucid.tools.OutBuffer import Redirector

from django import newforms as forms

import sys, os, StringIO



#______________________________________________________________________________

syncdb_template = """
{% extends "PyLucid/install/base.html" %}
{% block content %}
<h1>syncdb</h1>
<pre>{{ output|escape }}</pre>
{% endblock %}
"""
class Sync_DB(BaseInstall):
    def view(self):
        out = Redirector(sys.stderr)
        output = ["django syncdb..."]
        try:
            from django.core import management
            management.syncdb(verbosity=2, interactive=False)
        except Exception, e:
            sys.stderr.write("Error: %s\n" % e)
        
        output.append(out.get())
        output.append("done.")
        
        self.context["output"] = "".join(output)
        return self._render(syncdb_template)
    
def syncdb(request, install_pass):
    """
    1. install Db tables (syncdb)
    """
    return Sync_DB(request, install_pass).view()

#______________________________________________________________________________
class InitDBForm(forms.Form):
    """
    django newforms
    """
    from glob import glob
    fnmatch = os.path.join(settings.INSTALL_DATA_DIR, "initial_data.*")
    fixture_filenames = glob(fnmatch)
        
    fixture_file = forms.ChoiceField(
        choices=[(i,i) for i in fixture_filenames],
        widget=forms.RadioSelect,
        help_text='Please select a fixture file.'
    )

dump_template = """
{% extends "PyLucid/install/base.html" %}
{% block content %}
<h1>init DB</h1>

{% if output %}
    <fieldset><legend>{{ file_name|escape }}</legend>
        <pre>{{ output|escape }}</pre>
    </fieldset>
{% else %}
    <form method="post">
        {{ FormData }}
        <input value="execute" name="execute" type="submit">
    </form>
{% endif %}
{% endblock %}
"""
class Init_DB(BaseInstall):
    def view(self):
        if "fixture_file" in self.request.POST:
            # Form has been sended
            init_values = self.request.POST.copy()
        else:
            # Requested the first time -> insert a init codeblock
            init_values = None
            
        init_db_form = InitDBForm(init_values)
        init_db_html = init_db_form.as_p()
        
        self.context["FormData"] = init_db_html
        
        output = []
        if "fixture_file" in self.request.POST and init_db_form.is_valid():
            fixture_file = init_db_form.clean_data["fixture_file"]
            format = fixture_file.rsplit(".",1)[1]
            self.context["file_name"] = fixture_file
            
            output.append("Read fixture file '%s'..." % fixture_file)
            try:
                f = file(fixture_file, "rb")
        #        import codecs
        #        f = codecs.open(fixture_filename, "r", "utf-8")
                fixture = f.read()
        #        fixture = unicode(fixture, "utf8")
        #        #fixture = unicode(fixture, errors="replace")
                f.close()
            except Exception, e:
                output.append("Error: %s" % e)
            else:
                output.append("OK\n")
                
                from django.core import serializers
        
                objects = serializers.deserialize(format, fixture)
                
                count = 0
                for object in objects:
                    try:
                        object.save()
                    except Exception, e:
                        output.append("Error: %s\n" % e)
                    else:
                        count += 1
                    
                output.append("%s objects restored\n" % count)
        
        self.context["output"] = "".join(output)
        return self._render(dump_template)

def init_db(request, install_pass):
    """
    2. init DB data
    """
    return Init_DB(request, install_pass).view()
#______________________________________________________________________________

create_user_template = """
{% extends "PyLucid/install/base.html" %}
{% block content %}
<h1>Create test superuser</h1>
<pre>{{ output|escape }}</pre>
{% endblock %}
"""
class CreateTestUser(BaseInstall):
    def view(self):
        output = ["Create a 'test' superuser..."]
        from django.contrib.auth.models import User
        try:
            user = User.objects.create_user('test', 'test@invalid', '12345678')
        except Exception, e:
            output.append("ERROR: %s\n" % e)
        else:
            output.append("OK\n")
    
        output.append("\nSetup rights...")
        try:
            user = User.objects.get(username__exact='test')
            user.is_staff = True
            user.is_active = True
            user.is_superuser = True
            user.save()
        except Exception, e:
            output.append("ERROR: %s\n" % e)
        else:
            output.append("OK\n")

        self.context["output"] = "".join(output)
        return self._render(create_user_template)

def create_test_user(request, install_pass):
    """
    3. create test superuser
    """
    return CreateTestUser(request, install_pass).view()



    
