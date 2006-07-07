@echo off

:loop
    echo Starte Webserver...
    python PyLucid_app.py
    echo.
    pause
goto loop

pause