
clear
~\AppData\Local\Microsoft\WindowsApps\bat.exe  --color=always --theme=base16 $Args[0]

Write-Host -NoNewLine 'Press any key to continue...';
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown');

