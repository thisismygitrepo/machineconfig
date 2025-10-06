
@echo off
setlocal EnableDelayedExpansion EnableExtensions
goto main
:usage
echo No arguments specified. >&2
echo Usage: >&2
echo transfer ^<file^|directory^> >&2
echo ... ^| transfer ^<file_name^> >&2
exit /b 1
:main
if "%~1" == "" goto usage
timeout.exe /t 0 >nul 2>nul || goto not_tty
set "file=%~1"
for %%A in ("%file%") do set "file_name=%%~nxA"
if exist "%file_name%" goto file_exists
echo %file%: No such file or directory >&2
exit /b 1
:file_exists
if not exist "%file%\" goto not_a_directory
set "file_name=%file_name%.zip"
pushd "%file%" || exit /b 1
set "full_name=%temp%\%file_name%"
powershell.exe -Command "Get-ChildItem -Path . -Recurse | Compress-Archive -DestinationPath ""%full_name%"""
curl.exe --progress-bar --upload-file "%full_name%" "https://transfer.sh/%file_name%"
popd
goto :eof
:not_a_directory
curl.exe --progress-bar --upload-file "%file%" "https://transfer.sh/%file_name%"
goto :eof
:not_tty
set "file_name=%~1"
curl.exe --progress-bar --upload-file - "https://transfer.sh/%file_name%"
goto :eof
