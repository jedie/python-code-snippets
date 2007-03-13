
"""
1. install

sollte ich mir mal ansehen:
http://code.djangoproject.com/wiki/CookBookScriptsMiniFlush
"""

import sys, os, StringIO

from PyLucid.utils import check_pass
from PyLucid.settings import TABLE_PREFIX
from PyLucid.system.response import PyLucidResponse

from django.http import HttpResponse

#______________________________________________________________________________

def syncdb(request, install_pass):
    """
    1. install Db tables (syncdb)
    """
    check_pass(install_pass)

    response = PyLucidResponse(request, mimetype="text/plain")
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = response
    sys.stderr = response
    print "django syncdb..."
    try:
        from django.core import management
        management.syncdb(verbosity=2, interactive=False)
    except Exception, e:
        sys.stderr.write("Error: %s\n" % e)

    print "done."

    sys.stdout = old_stdout
    sys.stderr = old_stderr

    return response

#______________________________________________________________________________
format = "xml"
#format = "json"
#format = "python"
#format = "pyyaml"
def init_db(request, install_pass):
    """
    2. init DB data
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

#______________________________________________________________________________

def create_user(request, install_pass):
    """
    3. create test superuser
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




    
