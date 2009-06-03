@echo off
cd /d "%~dp0"
title %1
echo on

python.exe audio_remix.py %*

@echo off
echo.
title done - %1
pause