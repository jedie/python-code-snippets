@REM Only a small batch file to create the MAXScript ZIP Package (*.mzp File)
"%ProgramFiles%\7-Zip\7z.exe" u -tzip -mx9 MAXScript_ZIP_Package\ViewportSwitchFix.mzp *.ms *.mcr *.run *.txt
@pause