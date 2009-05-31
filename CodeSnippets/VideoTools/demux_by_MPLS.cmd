@cd /d "%~dp0"
@title %1
python.exe demux_by_MPLS.py %*
@pause