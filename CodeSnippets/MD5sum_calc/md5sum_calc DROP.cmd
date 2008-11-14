@REM
@REM Helper batch for windows.
@REM
@REM Put a link from this file on your desktop.
@REM Then you can easy drop files on the link.
cd /d "%~dp0"
python.exe md5sum_calc.py %*
@pause