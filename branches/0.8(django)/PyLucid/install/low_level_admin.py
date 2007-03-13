
"""
3. low level admin

sollte ich mir mal ansehen:
http://code.djangoproject.com/wiki/CookBookScriptsMiniFlush
"""

import sys, os, StringIO, pickle

from PyLucid.utils import check_pass
from PyLucid.settings import TABLE_PREFIX
from PyLucid.system.response import PyLucidResponse

from django.http import HttpResponse
from django.template import Template, Context, loader
from django import newforms as forms

from django.core import serializers

#______________________________________________________________________________

serializer_formats = serializers.get_serializer_formats()
class DumpForm(forms.Form):
    """
    django newforms
    """
    format = forms.ChoiceField(
        choices=[(i,i) for i in serializer_formats],
    )
    write_file = forms.BooleanField(initial=False, required=False)

dump_template = """
{% extends "PyLucid/install/base.html" %}
{% block content %}
<h1>Dump DB</h1>

<form method="post">
    {{ DumpForm }}
    <input value="execute" name="execute" type="submit">
</form>
{% if output %}
<fieldset><legend>{{ file_name|escape }}</legend>
    <pre>{{ output|escape }}</pre>
</fieldset>
{% endif %}
{% endblock %}
"""
def dump(request, install_pass):
    """
    dump db data
    """
    check_pass(install_pass)
    
    if "format" in request.POST:
        # Form has been sended
        init_values = request.POST.copy()
    else:
        # Requested the first time -> insert a init codeblock
        init_values = {
            "format": serializer_formats[0],
            "write_file": False,
        }
    
    dump_form = DumpForm(init_values)
    dump_form_html = dump_form.as_p()
    
    if (not "format" in request.POST) or (not dump_form.is_valid()):
        context = Context({
            "DumpForm": dump_form_html,
        })
        t = Template(dump_template)
        html = t.render(context)
        return HttpResponse(html)
    
    format = dump_form.clean_data["format"]
    write_file = dump_form.clean_data["write_file"]
    
    from django.db.models import get_app, get_apps, get_models
    from django.core import serializers
 
    app_list = get_apps()
 
    # Check that the serialization format exists; this is a shortcut to
    # avoid collating all the objects and _then_ failing.
    serializers.get_serializer(format)
    
    fixture_filename = "PyLucid/fixtures/initial_data.%s" % format
    if write_file:
        output = ["Open output file '%s'..." % fixture_filename]
        try:
            dumpfile = file(fixture_filename, "w")
        except Exception, e:
            output.append("Error: %s" % e)
            return response
        else:
            output.append("OK\n")
    
    objects = []
    for app in app_list:
        for model in get_models(app):
            model_objects = model.objects.all()
            objects.extend(model_objects)
        
    db_data = serializers.serialize(format, objects)
    
    if write_file:
        output.append("Write to file...")
        if format=="python":
            try:
                pickle.dump(db_data, dumpfile)
            except Exception, e:
                output.append("Error: %s" % e)
            else:
                output.append("OK\n")
        else:
            try:
                dumpfile.write(db_data)
            except Exception, e:
                output.append("Error: %s" % e)
            else:
                output.append("OK\n")
        dumpfile.close()
    else:
        if format=="xml":
            mimetype='text/xml'
        else:
            mimetype='text/plain'
        response = HttpResponse(mimetype=mimetype)
        response.write(db_data)
        return response

    context = Context({
        "DumpForm": dump_form_html,
        "output": "".join(output),
        "file_name": fixture_filename,
    })
    t = Template(dump_template)
    html = t.render(context)
    return HttpResponse(html)

