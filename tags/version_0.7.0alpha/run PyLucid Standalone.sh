#!/usr/bin/env sh
echo ${PWD}

while : # Null-Befehl (immer wahr)
do
    echo Starting Server...
    python PyLucid_app.py
    echo ----------------------------------------
    echo Restart in 3 Sec...
    sleep 3 # sleep: warten
done
