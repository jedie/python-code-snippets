
"""
Clean up django tables

http://groups.google.com/group/django-developers/browse_thread/thread/50073e3a377dcd80
http://www.python-forum.de/topic-10510.html
"""

if __name__ == "__main__": # Init django
    from PyLucid import settings

    from django.core.management import setup_environ
    setup_environ(settings)

from django.db.models import get_apps, get_app, get_models
from django.db import connection


def clean_contenttypes(debug=True):
    """
    Delete all contenttypes in the table 'django_content_type' if the
    corresponding model doesn't exist for this type.

    This happens, when you remove applications from your project or if you
    delete some model class in your app.
    """
    print "Delete obsolete django 'content types'...\n"

    cursor = connection.cursor()

    db_types = {}
    cursor.execute("SELECT id, model FROM django_content_type")
    for id, model in cursor.fetchall():
        db_types[model] = id
    print "db_types: %s" % repr(db_types)

    model_names = []
    for app in get_apps():
        for model in get_models(app):
            model = model._meta.object_name
            model = model.lower()
            model_names.append(model)

    print "model_names: %s" % repr(model_names)

    db_type_names = set(db_types.keys())
    model_names = set(model_names)

    obsolete_names = db_type_names - model_names
    print "obsolete_names: %s" % repr(obsolete_names)

    SQLcommand = "DELETE FROM django_content_type WHERE id = %s;"
    for model in obsolete_names:
        id = db_types[model]
        print "delete: %s - id: %s" % (model, id)
        if debug:
            print "Debug only:"
            print SQLcommand % id
        else:
            cursor.execute(SQLcommand, [id])
    else:
        print "\nTable 'django_content_type' up to date. Nothing to do."


def clean_permissions(debug=True):
    """
    Deletes all permission entries in the table 'auth_permission' if there is
    no contenttype for it.
    """
    print "Delete obsolete django 'permissions'...\n"

    cursor = connection.cursor()

    cursor.execute("SELECT id FROM django_content_type;")
    db_content_ids = [i[0] for i in cursor.fetchall()]
    print "db_content_ids: %s" % repr(db_content_ids)

    cursor.execute("SELECT content_type_id, codename FROM auth_permission;")
    db_permissions = {}
    for id, permission in cursor.fetchall():
        if not id in db_permissions:
            db_permissions[id] = []
        db_permissions[id].append(permission)
    print "db_permissions: %s" % repr(db_permissions)

    SQLcommand = "DELETE FROM auth_permission WHERE content_type_id = %s;"
    uptodate = True
    for id, permission in db_permissions.iteritems():
        if id in db_content_ids:
            continue
        print "obsolete permissions: %s: %s" % (id, permission)
        uptodate = False
        if debug:
            print "Debug only:"
            print SQLcommand % id
        else:
            cursor.execute(SQLcommand, [id])
    if uptodate:
        print "\nTable 'auth_permission' up to date. Nothing to do."

if __name__ == "__main__":
    debug = True

    clean_contenttypes(debug)
    print
    clean_permissions(debug)

