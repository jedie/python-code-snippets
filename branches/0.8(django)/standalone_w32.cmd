@echo off

REM Startet einen lokalen Test-Server.

REM Evtl. mu� der Pfad zur python.exe angepasst werden, wenn
REM der Python-Interpreter nicht im Pfad ist!

REM ~ set DJANGO_SETTINGS_MODULE=PyLucid.settings

:loop
    echo Starte Webserver...

    REM f�r Python 2.4:
    python .\django\bin\django-admin.py runserver --settings=PyLucid.settings

    REM f�r Python <2.4:
    REM python PyLucid_app_withBackports.py

    echo.
    echo Restart des Server:
    pause
goto loop

pause