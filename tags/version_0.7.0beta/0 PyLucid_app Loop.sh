#!/bin/sh

while :
do
    echo 'Starte Webserver...'
    python PyLucid_app.py
    echo ''
    echo 'Enter dr�cken!'
    read
done

echo 'Enter zum Beenden.'
read