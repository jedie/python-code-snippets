@echo off

REM ~ set DJANGO_SETTINGS_MODULE=PyLucid.settings

:loop
    echo Starting django development server...

    python .\django\bin\django-admin.py runserver --settings=PyLucid.settings --pythonpath=.

    echo.
    echo Restart des Server:
    pause
goto loop

pause