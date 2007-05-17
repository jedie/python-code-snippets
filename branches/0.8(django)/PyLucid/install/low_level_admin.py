
"""
3. low level admin

sollte ich mir mal ansehen:
http://code.djangoproject.com/wiki/CookBookScriptsMiniFlush
"""

import pickle

from PyLucid import settings

from PyLucid.install.BaseInstall import BaseInstall

from django import newforms as forms
from django.core import serializers




#______________________________________________________________________________

#===============================================================================
#serializer_formats = serializers.get_serializer_formats()
#class DumpForm(forms.Form):
#    """
#    django newforms
#    """
#    format = forms.ChoiceField(
#        choices=[(i,i) for i in serializer_formats],
#    )
#    write_file = forms.BooleanField(initial=False, required=False)
#
#dump_template = """
#{% extends "PyLucid/install/base.html" %}
#{% block content %}
#<h1>Dump DB</h1>
#
#<form method="post">
#    {{ DumpForm }}
#    <input value="execute" name="execute" type="submit">
#</form>
#{% if output %}
#<fieldset><legend>{{ file_name|escape }}</legend>
#    <pre>{{ output|escape }}</pre>
#</fieldset>
#{% endif %}
#{% endblock %}
#"""
#class Dump_DB(BaseInstall):
#    def view(self):
#        if "format" in self.request.POST:
#            # Form has been sended
#            init_values = self.request.POST.copy()
#        else:
#            # Requested the first time -> insert a init codeblock
#            init_values = {
#                "format": serializer_formats[0],
#                "write_file": False,
#            }
#
#        dump_form = DumpForm(init_values)
#
#        dump_form_html = dump_form.as_p()
#        self.context["DumpForm"] = dump_form_html
#
#        if (not "format" in self.request.POST) or (not dump_form.is_valid()):
#            # Requested the first time -> display the form
#            return self._render(dump_template)
#
#        format = dump_form.clean_data["format"]
#        write_file = dump_form.clean_data["write_file"]
#
#        from django.db.models import get_app, get_apps, get_models
#        from django.core import serializers
#
#        app_list = get_apps()
#
#        # Check that the serialization format exists; this is a shortcut to
#        # avoid collating all the objects and _then_ failing.
#        serializers.get_serializer(format)
#
#        fixture_filename = "PyLucid/fixtures/initial_data.%s" % format
#        self.context["file_name"] = fixture_filename
#        if write_file:
#            output = ["Open output file '%s'..." % fixture_filename]
#            try:
#                dumpfile = file(fixture_filename, "w")
#            except Exception, e:
#                output.append("Error: %s" % e)
#                return response
#            else:
#                output.append("OK\n")
#
#        objects = []
#        for app in app_list:
#            for model in get_models(app):
#                model_objects = model.objects.all()
#                objects.extend(model_objects)
#
#        db_data = serializers.serialize(format, objects)
#
#        if write_file:
#            output.append("Write to file...")
#            if format=="python":
#                try:
#                    pickle.dump(db_data, dumpfile)
#                except Exception, e:
#                    output.append("Error: %s" % e)
#                else:
#                    output.append("OK\n")
#            else:
#                try:
#                    dumpfile.write(db_data)
#                except Exception, e:
#                    output.append("Error: %s" % e)
#                else:
#                    output.append("OK\n")
#            dumpfile.close()
#        else:
#            if format=="xml":
#                mimetype='text/xml'
#            else:
#                mimetype='text/plain'
#            response = HttpResponse(mimetype=mimetype)
#            response.write(db_data)
#            return response
#
#        self.context["output"] = "".join(output)
#        return render(dump_template)
#
#def _dump_db(request, install_pass):# deactivated with the unterscore!
#    """
#    dump db data (using fixture)
#    """
#    return Dump_DB(request, install_pass).view()
#===============================================================================

#______________________________________________________________________________

class Options(object):
    """ Fake optparse options """
    def __init__(self):
        self.datadir = settings.INSTALL_DATA_DIR
        self.verbose = True
        self.stdout = None
        self.remain = None
        self.settings = "PyLucid.settings"

class Dump_DB(BaseInstall):
    def view(self):
        from PyLucid.tools.db_dump import dumpdb
        apps = []

        self._redirect_execute(
            dumpdb, apps, 'py', Options()
        )

        return self._simple_render(headline="DB dump (using db_dump.py)")

def dump_db(request, install_pass):
    """
    dump db data (using db_dump.py)
    """
    return Dump_DB(request, install_pass).view()

#______________________________________________________________________________

class CleanupDjangoTables(BaseInstall):
    def view(self):
        from PyLucid.tools.clean_tables import clean_contenttypes, clean_permissions
        self._redirect_execute(
            clean_contenttypes, debug=False
        )
        self.context["output"] += "\n\n"
        self._redirect_execute(
            clean_permissions, debug=False
        )
        return self._simple_render(headline="Cleanup django tables")


def cleanup_django_tables(request, install_pass):
    """
    cleanup django tables
    """
    return CleanupDjangoTables(request, install_pass).view()