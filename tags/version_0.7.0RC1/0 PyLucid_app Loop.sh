#!/bin/sh

while :
do
    echo 'Starte Webserver...'
    python PyLucid_app.py
    echo ''
    echo 'Enter drücken!'
    read
done

echo 'Enter zum Beenden.'
read