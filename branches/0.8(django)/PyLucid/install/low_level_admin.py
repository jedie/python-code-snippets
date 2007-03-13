
"""
1. low level admin

sollte ich mir mal ansehen:
http://code.djangoproject.com/wiki/CookBookScriptsMiniFlush
"""

import sys, os, StringIO

from PyLucid.utils import check_pass
from PyLucid.settings import TABLE_PREFIX
from PyLucid.system.response import PyLucidResponse

from django.http import HttpResponse

#______________________________________________________________________________

def create_user(request, install_pass):
    """
    Create Test superuser
    """
    check_pass(install_pass)
    
    response = HttpResponse(mimetype="text/plain")
    response.write("Create a 'test' superuser...")
    from django.contrib.auth.models import User
    try:
        user = User.objects.create_user('test', 'test@invalid', '12345678')
    except Exception, e:
        response.write("ERROR: %s\n" % e)
    else:
        response.write("OK\n")

    response.write("\nSetup rights...")
    try:
        user = User.objects.get(username__exact='test')
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save()
    except Exception, e:
        response.write("ERROR: %s\n" % e)
    else:
        response.write("OK\n")

    return response

#______________________________________________________________________________
format = "xml"
#format = "json"
#format = "python"
#format = "pyyaml"
def init_db(request, install_pass):
    """
    1. init db
    """
    check_pass(install_pass)
    response = HttpResponse(mimetype="text/plain")
    
    fixture_filename = "PyLucid/fixtures/initial_data.%s" % format
    f = file(fixture_filename, "r")
    fixture = f.read()
    f.close()
    
    from django.core import serializers
    #print serializers.get_serializer_formats()
    #serializer = serializers.get_serializer("python")
    objects = serializers.deserialize(format, fixture)
    
    count = 0
    for object in objects:
        try:
            object.save()
        except Exception, e:
            response.write("Error: %s\n" % e)
        else:
            count += 1
        
    response.write("%s objects restored\n" % count)
    
    return response

def dump(request, install_pass):
    """
    dump db data
    """
    check_pass(install_pass)
    response = HttpResponse(mimetype="text/plain") 
    
    from django.db.models import get_app, get_apps, get_models
    from django.core import serializers
 
    app_list = get_apps()
 
    # Check that the serialization format exists; this is a shortcut to
    # avoid collating all the objects and _then_ failing.
    serializers.get_serializer(format)
    
    fixture_filename = "PyLucid/fixtures/initial_data.%s" % format
    response.write("Open output file '%s'..." % fixture_filename)
    try:
        dumpfile = file(fixture_filename, "w")
    except Exception, e:
        response.write("Error: %s" % e)
        return response
    else:
        response.write("OK\n")
    
    objects = []
    for app in app_list:
        for model in get_models(app):
            model_objects = model.objects.all()
            response.write(repr(model_objects))
            objects.extend(model_objects)
        
    return response

    output = serializers.serialize(format, objects)
    
    response.write("Write...")
    if format=="python":
        import pickle
#        try:
        output = pickle.dump(output, dumpfile)
#        except Exception, e:
#            response.write("Error: %s" % e)
#            return response
#        else:
#            response.write("OK\n")
    else:
        dumpfile.write(output)
        dumpfile.close()
            
    response.write("DB Dump written (%sBytes).\n")
    return response
    
