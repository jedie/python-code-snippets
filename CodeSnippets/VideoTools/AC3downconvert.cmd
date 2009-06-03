@echo off
cd /d "%~dp0"
title %1
echo on

python.exe AC3downconvert.py %*

@echo off
echo.
title done - %1
pause