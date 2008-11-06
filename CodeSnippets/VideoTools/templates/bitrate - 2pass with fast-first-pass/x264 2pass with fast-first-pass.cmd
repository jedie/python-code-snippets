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

set pass1_source=${basename} DirectShowSource pass1.avs
set pass2_source=${basename} DirectShowSource pass2.avs

set rate_value=${rate_value}
set stats_file=${basename} x264.stats

set out_file1=${basename} x264 ${rate_value}KBits pass1.mkv
set out_file2=${basename} x264 ${rate_value}KBits pass2.mkv

REM x264 settings:        
set firstpass=${firstpass}
set finalpass=${finalpass} 

REM --------------------------------------------------------------------------

call:check_exist "%pass1_source%"
call:check_exist "%pass2_source%"

if exist "%stats_file%" (
    echo Skip pass 1, file "%stats_file%" exists.
    goto pass2
)

:pass1
echo on
%x264% --pass 1 %firstpass% --bitrate %rate_value% --stats "%stats_file%" -o "%out_file1%" "%pass1_source%"
@echo off

:pass2
echo on
%x264% --pass 2 %finalpass% --bitrate %rate_value% --stats "%stats_file%" -o "%out_file2%" "%pass2_source%"
@echo off

title Fertig: ${video_file_path} 
echo.
pause
goto:eof

:check_exist
    if not exist "%~1" (
        call:error "File [%1] doesn't exist!"
        exit
    )
goto:eof

:error
    echo Error:
    echo %1
    echo.
    pause
goto:eof
