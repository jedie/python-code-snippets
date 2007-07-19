
"""
1. install

sollte ich mir mal ansehen:
http://code.djangoproject.com/wiki/CookBookScriptsMiniFlush
"""

from PyLucid import settings
from PyLucid.install.BaseInstall import BaseInstall

from django import newforms as forms
from django.contrib.auth.models import User

import sys, os

#______________________________________________________________________________

syncdb_template = """
{% extends "install_base.html" %}
{% block content %}
<h1>syncdb</h1>
<pre>{{ output|escape }}</pre>
{% endblock %}
"""
class Sync_DB(BaseInstall):

    # Drop this tables before syncdb:
    DROP_TABLES = ("PyLucid_preference",)

    def view(self):
        from django.core import management
        # Output without escape sequences:
        management.disable_termcolors()

        self._redirect_execute(self.drop_tables, management)
        self._redirect_execute(self.syncdb, management)
        return self._render(syncdb_template)

    def drop_tables(self, management):
        print
        print "drop tables:"
        print "-"*80
        from django.db import connection
        from django.db.models import get_app

        app = get_app("PyLucid")
        statements = management.get_sql_delete(app)

        cursor = connection.cursor()
        for statement in statements:
            for table_name in self.DROP_TABLES:
                if table_name in statement:
                    print "Delete table '%s' (%s):" % (table_name, statement),
                    try:
                        cursor.execute(statement)
                    except Exception, e:
                        print "Error:", e
                    else:
                        print "OK"
        print "-"*80

    def syncdb(self, management):
        print
        print "syncdb:"
        print "-"*80
        management.syncdb(verbosity=1, interactive=False)
        print "-"*80
        print "syncdb ok."


def syncdb(request):
    """
    1. install Db tables (syncdb, Note: old preferences lost!)
    """
    return Sync_DB(request).start_view()

#______________________________________________________________________________

class DB_DumpFakeOptions(object):
    """ Fake optparse options """
    datadir = 'PyLucid/db_dump_datadir'
    verbose = True
    stdout = None
    # Remain the records of the tables, default will delete all the records:
    remain = True
    settings = "PyLucid.settings"

class Init_DB2(BaseInstall):
    def view(self):
        from PyLucid.tools.db_dump import loaddb

        # Delete all prefecrences (only for alpha state!!!)
        from PyLucid.models import Preference
        Preference.objects.all().delete()

        self._redirect_execute(
            loaddb,
            app_labels = [], format = "py", options = DB_DumpFakeOptions()
        )

        return self._simple_render(headline="init DB (using db_dump.py)")

def init_db2(request):
    """
    2. init DB data (using db_dump.py, Note: old preferences lost!)
    TODO: In the final we should not delete the preferences!
    """
    return Init_DB2(request).start_view()

#______________________________________________________________________________

install_modules_template = """
{% extends "install_base.html" %}
{% block content %}
<h1>Install all internal plugins:</h1>
<pre>{{ output|escape }}</pre>
{% endblock %}
"""
class InstallPlugins(BaseInstall):
    def view(self):
        output = []
        from PyLucid.system import plugin_manager

        self._redirect_execute(plugin_manager.install_internal_plugins)

        return self._render(install_modules_template)

def install_plugins(request):
    """
    3. install internal plugins
    """
    return InstallPlugins(request).start_view()

#______________________________________________________________________________

create_user_template = """{% load i18n %}
{% extends "install_base.html" %}
{% block content %}
<h1>{% trans 'Add user' %}</h1>

{% if output %}
    <pre>{{ output|escape }}</pre>
{% endif %}

<form method="post">
  <table class="form">
    {{ form }}
  </table>
  <ul>
      <strong>{% trans 'Note' %}:</strong>
      <li>
        {% blocktrans %}Every User you create here,
        is a superuser how can do everything!{% endblocktrans %}
      </li>
      <li>
        {% blocktrans %}After you have created the first user,
        you can login and create normal user, using{% endblocktrans %}
        <a href="/{{ admin_url_prefix }}/auth/user/">{% trans 'Django administration' %}</a>.
      </li>
  </ul>
  <input type="submit" value="{% trans 'Add user' %}" />
</form>

{% endblock %}
"""
class CreateUser(BaseInstall):
    def view(self):
        """
        Display the user form.
        """
        UserForm = forms.form_for_model(
            User,
            fields=("username", "first_name", "last_name", "email", "password")
        )
        # Change the help_text, because there is a URL in the default text
        UserForm.base_fields['password'].help_text = ""

        if self.request.method == 'POST':
            user_form = UserForm(self.request.POST)
            if user_form.is_valid():
                # Create the new user
                self._redirect_execute(self.create_user, user_form)
        else:
            user_form = UserForm()

        self.context["form"] = user_form.as_table()
        self.context["admin_url_prefix"] = settings.ADMIN_URL_PREFIX

        return self._render(create_user_template)

    def create_user(self, user_form):
        """
        create a new user in the database
        """
        print "Create a new superuser:"

        user_data = user_form.cleaned_data
        try:
            user = User.objects.create_user(
                user_data["username"], user_data["email"], user_data["password"]
            )
            user.is_staff = True
            user.is_active = True
            user.is_superuser = True
            user.first_name = user_data["first_name"]
            user.last_name = user_data["last_name"]
            user.save()
        except Exception, e:
            print "ERROR: %s" % e
        else:
            print "OK"


def create_user(request):
    """
    4. create the first superuser
    """
    return CreateUser(request).start_view()


