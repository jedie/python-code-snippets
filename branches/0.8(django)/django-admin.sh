#!/bin/sh

#export DJANGO_SETTINGS_MODULE=PyLucid.settings

python ./django/bin/django-admin.py --settings=PyLucid.settings --pythonpath=. $*