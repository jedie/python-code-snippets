#!/bin/sh

# Startet einen lokalen Test-Server.

#export DJANGO_SETTINGS_MODULE=PyLucid.settings

while :
do
    echo 'Starte Webserver...'

    django-admin.py runserver --settings=PyLucid.settings --pythonpath=${PWD}

    ping localhost -n 1>NUL

    echo ''
    echo 'restart des Servers mit ENTER...'
    read
done

echo 'ENTER zum Beenden.'
read
