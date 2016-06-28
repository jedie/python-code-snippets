@echo off
title %~0

set BASE_PATH=%ProgramFiles%\Autodesk\3ds Max 2017
call:test_exist "%BASE_PATH%" "max 2017 not found here:"

cd /d %BASE_PATH%

set SCRIPT_PATH=%BASE_PATH%\python\Scripts
echo.
echo add to PATH: %SCRIPT_PATH%
set PATH=%SCRIPT_PATH%;%PATH%

set PYTHON=3dsmaxpy.exe
call:test_exist "%PYTHON%" "3dsmaxpy.exe not found here:"

echo.
echo on
%PYTHON% --version
pip.exe --version
@echo off

whoami /groups | find "S-1-16-12288" > nul
if errorlevel 1 (
    echo.
    echo WARNING: Start as Admin if you would like to use pip!
    echo.
) else (
    echo.
    echo on
    pip.exe install --upgrade pip
    @echo off
)

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
