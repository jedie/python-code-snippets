@echo off

cd \

if exist %windir%\SysWOW64\ (
    REM WOW64 exist -> a 64 bit system
    call:open "%APPDATA%\Microsoft\Windows\SendTo\"

) ELSE (
    REM There is no WOW64 -> a 32 bit system
    call:open "%ALLUSERSPROFILE%\SendTo\"
)
echo pause...
ping localhost>NUL
goto:eof

:open
    echo on
    start explorer %1
    @echo off
goto:eof

