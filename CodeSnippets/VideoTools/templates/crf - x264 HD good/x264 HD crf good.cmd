@echo off
title %~0 [${video_file_path}]

if "%1"=="" (
    REM Start process with low priority
    start /WAIT /LOW /B cmd.exe /V /C %~s0 continue
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

if not exist "%source_file%" (
    call:error "File [%source_file%] doesn't exist!"
    goto:eof
)
if exist "%out_file%" (
    call:error "File [%out_file%] exist!"
    goto:eof
)

echo on
%x264% %finalpass% --crf %rate_value% -o "%out_file%" "%source_file%"
@echo off

title Fertig: ${video_file_path} 
pause
goto:eof

:error
    echo Error:
    echo %1
    echo.
    pause
goto:eof