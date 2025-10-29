
REM adopted from https://github.com/phiresky/ripgrep-all/wiki/fzf-Integration

@echo off
setlocal

set RG_PREFIX=rga --files-with-matches 
set FZF_DEFAULT_COMMAND=%RG_PREFIX% %1 
for /f  "delims=" %%i in ('fzf --sort --preview "rga --pretty --context 5 {q} {}" --phony -q %1 --bind "change:reload:%RG_PREFIX% {q}" --preview-window="70%:wrap"') do (
    set FILE=%%i
)

if not "%FILE%" == "" (
    echo Opening %FILE%
    start "" "%FILE%"
) else (
    echo No file selected.
)

endlocal
