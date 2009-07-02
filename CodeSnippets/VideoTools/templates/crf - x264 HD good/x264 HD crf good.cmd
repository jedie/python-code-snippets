@echo off
title %~0 [${video_file_path}]

if "%1"=="" (
    REM Start process with low priority
    start /WAIT /LOW /B cmd.exe /V /C "%~s0" continue
    goto:eof
)

REM --------------------------------------------------------------------------
REM Values setup by Templatemaker.py

set x264=${x264}
set source_file=${basename} DirectShowSource.avs
set rate_value=${rate_value}
set out_file=${basename} x264 crf${rate_value}.mkv

REM x264 settings:
set finalpass=${finalpass}

REM --------------------------------------------------------------------------

call:check_exist "%source_file%"
if exist "%out_file%" (
    call:error File [%out_file%] exist!
    exit
)

echo on
%x264% %finalpass% --crf %rate_value% -o "%out_file%" "%source_file%"
@echo off

title Fertig: ${video_file_path}
pause
goto:eof

:check_exist
    if not exist "%~1" (
        call:error File [%~1] doesn't exist!
        exit
    )
goto:eof

:error
    echo Error:
    echo %*
    echo.
    pause
goto:eof