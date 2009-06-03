@echo off
cd /d "%~dp0"
title %1
echo on

python.exe Templatemaker.py %*

@echo off
echo.
title done - %1
echo pause...
ping localhost>NUL