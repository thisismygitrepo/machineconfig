@ECHO OFF
REM
REM LF Archive Extract script
REM
REM Use 7zip for extractor
REM
REM Extract archive contents into destination folder 
REM with the same name as the archive file
REM

7z x %1 -o%~n1 -y 1> %LOCALAPPDATA%\lf\extract.log 2>&1
