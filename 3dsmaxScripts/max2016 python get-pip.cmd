@echo off
title %~0
cd /d c:\

whoami /groups | find "S-1-16-12288" > nul
if errorlevel 1 (
   echo Fehler: Dieses Skript muss mit Administratorrechten aufgerufen werden.
   pause
   exit /b
)

set BASE_PATH=%ProgramFiles%\Autodesk\3ds Max 2016
call:test_exist "%BASE_PATH%" "max 2016 not found here:"

echo on
cd /d %BASE_PATH%
@echo off

set PYTHON=python\python.exe
call:test_exist "%PYTHON%" "python.exe not found here:"

echo.
echo on
%PYTHON% --version
@echo off


set GETPIP=%temp%\get-pip.py

echo.
echo Download 'get-pip.py'
echo on
%PYTHON% -c "import urllib; print urllib.urlopen('https://bootstrap.pypa.io/get-pip.py').read()" > "%GETPIP%"
@echo off

call:test_exist "%GETPIP%" "Error downloading get-pip.py, not found here:"

echo on
cd /d %BASE_PATH%
%PYTHON% %GETPIP%
python\Scripts\pip.exe --version
del %GETPIP%
@echo off

echo.
echo pip installed.
title end - %~0
pause
goto:eof


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
