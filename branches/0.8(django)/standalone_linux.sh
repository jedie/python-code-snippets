#!/bin/sh

#export DJANGO_SETTINGS_MODULE=PyLucid.settings

while :
do
    echo 'Starting django development server...'

    python ./django/bin/django-admin.py runserver --settings=PyLucid.settings --pythonpath=.

    ping localhost -n 1>NUL

    echo ''
    echo 'restart des Servers mit ENTER...'
    read
done

echo 'ENTER zum Beenden.'
read
