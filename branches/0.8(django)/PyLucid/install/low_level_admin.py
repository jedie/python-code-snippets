
"""
installation

sollte ich mir mal ansehen:
http://code.djangoproject.com/wiki/CookBookScriptsMiniFlush
"""

import sys

import os

from PyLucid.utils import check_pass
from PyLucid.settings import TABLE_PREFIX
from PyLucid.system.response import PyLucidResponse

from django.http import HttpResponse

def syncdb(request, install_pass):
    """
    django syncdb
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


def update(request, install_pass):
    """
    update DB tables from v0.7.2 to django PyLucid v0.8
    """
    check_pass(install_pass)
    
    response = HttpResponse(mimetype="text/plain")
    response.write("update PyLucid database:\n")

    from django.db import connection
    cursor = connection.cursor()

    tablenames = (
        ("pages",  "page"),
        ("styles", "style"),
        ("templates", "template"),
        ("groups", "group"),
        ("markups", "markup"),
        ("md5users", "md5user"),
        ("plugins", "plugin"),
        ("preferences", "preference"),
        ("styles", "style"),
        ("template_engines", "template_engine"),
        ("templates", "template"),
    )
    for source, destination in tablenames:
        source = TABLE_PREFIX + source
        destination = TABLE_PREFIX + destination

        SQLcommand = "RENAME TABLE %s TO %s;" % (source, destination)
        response.write("%s..." % SQLcommand)
        try:
            cursor.execute(SQLcommand)
        except Exception, e:
            response.write("Error: %s\n" % e)
        else:
            response.write("OK\n")

    return response


