@echo off
title %~0

call:test_exist "%ProgramFiles%\Autodesk\3ds Max 2016" "max 2016 not found here:"

set BASE_PATH=%ProgramFiles%\Autodesk\3ds Max 2016\python
call:test_exist "%BASE_PATH%" "python dir not found here:"

echo on
cd /d %BASE_PATH%
@echo off

set PYTHON=python.exe
call:test_exist "%PYTHON%" "python.exe not found here:"

echo.

%PYTHON% --version
Scripts\pip.exe --version
cmd.exe /K echo Have python fun!
title end - %~0
pause
@goto:eof


:test_exist
    if NOT exist "%~1" (
        echo.
        echo ERROR: %~2
        echo.
        echo "%~1"
        echo.
        pause
        exit 1
    )
goto:eof
