@REM Only a small batch file to create the MAXScript ZIP Package (*.mzp File)
@set filename=MAXScript_ZIP_Package\ViewportSwitchFix.mzp
del %filename%
"%ProgramFiles%\7-Zip\7z.exe" u -tzip -mx9 %filename% *.ms *.mcr *.run *.txt
@pause