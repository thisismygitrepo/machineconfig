import typer
from typing import Optional, Annotated


def install_ssh_server() -> None:
    """📡 Install SSH server"""
    import platform
    if platform.system() == "Windows":
        script = _get_windows_ssh_server_install_script()
    elif platform.system() == "Linux" or platform.system() == "Darwin":
        script = """
sudo nala install openssh-server -y || true  # try to install first
# sudo nala purge openssh-server -y
# sudo nala install openssh-server -y
echo "✅ FINISHED installing openssh-server."
"""
    else:
        raise NotImplementedError(f"Platform {platform.system()} is not supported.")
    from machineconfig.utils.code import run_shell_script
    run_shell_script(script=script)


def change_ssh_port(port: Annotated[int, typer.Option(..., "--port", "-p", help="SSH port to use")] = 2222) -> None:
    """🔌 Change SSH port (Linux/WSL only, default: 2222)"""
    import platform
    if platform.system() != "Linux":
        raise NotImplementedError("change_ssh_port requires Linux environment")
    from machineconfig.utils.ssh_utils.wsl import change_ssh_port as _change_ssh_port
    _change_ssh_port(port=port)


def _get_windows_ssh_server_install_script(use_winget: bool = True) -> str:
    install_winget = r'''
    Write-Host "Installing OpenSSH via winget..." -ForegroundColor Cyan
    winget install --no-upgrade --Id Microsoft.OpenSSH.Preview --source winget --accept-package-agreements --accept-source-agreements
    $wingetSshPath = "C:\Program Files\OpenSSH"
    $currentMachinePath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    if ($currentMachinePath -notlike "*$wingetSshPath*") {
        Write-Host "Adding OpenSSH to system PATH..." -ForegroundColor Yellow
        [System.Environment]::SetEnvironmentVariable("Path", "$currentMachinePath;$wingetSshPath", "Machine")
    }
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
'''
    install_capability = r'''
    Write-Host "Installing OpenSSH via Windows Capability..." -ForegroundColor Cyan
    Add-WindowsCapability -Online -Name OpenSSH.Server
    Add-WindowsCapability -Online -Name OpenSSH.Client
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
'''
    configure_sshd_service = r'''
    $serviceExists = Get-Service -Name sshd -ErrorAction SilentlyContinue
    if (-not $serviceExists) {
        Write-Host "sshd service not found, registering manually..." -ForegroundColor Yellow
        sc.exe create sshd binPath= "$sshdExePath" start= auto
        if ($LASTEXITCODE -ne 0) { throw "Failed to create sshd service" }
    }
    Set-Service -Name sshd -StartupType Automatic
    Start-Service sshd
    Write-Host "sshd service started successfully." -ForegroundColor Green
'''
    configure_firewall = r'''
    $existingRule = Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -ErrorAction SilentlyContinue
    if (-not $existingRule) {
        Write-Host "Creating firewall rule for SSH..." -ForegroundColor Yellow
        New-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -DisplayName "OpenSSH SSH Server" -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 -Program $sshdExePath
    } else {
        Write-Host "Firewall rule already exists." -ForegroundColor Green
    }
'''
    configure_default_shell = r'''
    Write-Host "Configuring default shell for SSH..." -ForegroundColor Cyan
    $shell = "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
    if (-not (Test-Path "HKLM:\SOFTWARE\OpenSSH")) { New-Item -Path "HKLM:\SOFTWARE\OpenSSH" -Force | Out-Null }
    New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShell -Value $shell -PropertyType String -Force | Out-Null
    New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShellCommandOption -Value "/c" -PropertyType String -Force | Out-Null
    Write-Host "Default shell set to: $shell" -ForegroundColor Green
'''
    configure_ssh_agent = r'''
    Write-Host "Configuring ssh-agent service..." -ForegroundColor Cyan
    $agentService = Get-Service -Name ssh-agent -ErrorAction SilentlyContinue
    if ($agentService) {
        Set-Service -Name ssh-agent -StartupType Automatic
        Start-Service ssh-agent -ErrorAction SilentlyContinue
        Write-Host "ssh-agent service configured and started." -ForegroundColor Green
    } else {
        Write-Host "ssh-agent service not available." -ForegroundColor Yellow
    }
'''
    ensure_ssh_directory = r'''
    $sshDir = Join-Path $env:USERPROFILE ".ssh"
    if (-not (Test-Path $sshDir)) {
        New-Item -ItemType Directory -Path $sshDir -Force | Out-Null
        Write-Host "Created .ssh directory at: $sshDir" -ForegroundColor Green
    }
'''
    if use_winget:
        install_method = install_winget
        sshd_exe_path = r'C:\Program Files\OpenSSH\sshd.exe'
    else:
        install_method = install_capability
        sshd_exe_path = r'$env:WINDIR\System32\OpenSSH\sshd.exe'
    return fr'''
$ErrorActionPreference = "Stop"
try {{ Set-ExecutionPolicy -Scope CurrentUser Bypass -ErrorAction SilentlyContinue }} catch {{ }}
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "OpenSSH Server Installation for Windows" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
{install_method}
$sshdExePath = "{sshd_exe_path}"
{configure_sshd_service}
{configure_firewall}
{configure_default_shell}
{configure_ssh_agent}
{ensure_ssh_directory}
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "OpenSSH Server installation complete!" -ForegroundColor Green
Write-Host "SSH config directory: $env:ProgramData\ssh" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Magenta
'''


def add_ssh_key(
    path: Annotated[Optional[str], typer.Option(..., help="Path to the public key file")] = None,
    choose: Annotated[bool, typer.Option(..., "--choose", "-c", help="Choose from available public keys in ~/.ssh/*.pub")] = False,
    value: Annotated[bool, typer.Option(..., "--value", "-v", help="Paste the public key content manually")] = False,
    github: Annotated[Optional[str], typer.Option(..., "--github", "-g", help="Fetch public keys from a GitHub username")] = None,
) -> None:
    """🔑 Add SSH public key to this machine so its accessible by owner of corresponding private key."""
    import machineconfig.scripts.python.helpers.helpers_network.ssh_add_ssh_key as helper
    helper.main(pub_path=path, pub_choose=choose, pub_val=value, from_github=github)


def add_ssh_identity() -> None:
    """🗝️ Add SSH identity (private key) to this machine"""
    import machineconfig.scripts.python.helpers.helpers_network.ssh_add_identity as helper
    helper.main()


def debug_ssh() -> None:
    """🐛 Debug SSH connection"""
    from platform import system
    if system() == "Linux" or system() == "Darwin":
        import machineconfig.scripts.python.helpers.helpers_network.ssh_debug_linux as helper
        helper.ssh_debug_linux()
    elif system() == "Windows":
        import machineconfig.scripts.python.helpers.helpers_network.ssh_debug_windows as helper
        helper.ssh_debug_windows()
    else:
        raise NotImplementedError(f"Platform {system()} is not supported.")


def get_app() -> typer.Typer:
    ssh_app = typer.Typer(help="🔐 SSH subcommands", no_args_is_help=True, add_help_option=True, add_completion=False)
    ssh_app.command(name="install-server", help="📡 [i] Install SSH server")(install_ssh_server)
    ssh_app.command(name="i", help="Install SSH server", hidden=True)(install_ssh_server)
    ssh_app.command(name="change-port", help="🔌 [p] Change SSH port (Linux/WSL only)")(change_ssh_port)
    ssh_app.command(name="p", help="Change SSH port", hidden=True)(change_ssh_port)
    ssh_app.command(name="add-key", help="🔑 [k] Add SSH public key to this machine", no_args_is_help=True)(add_ssh_key)
    ssh_app.command(name="k", help="Add SSH public key to this machine", hidden=True, no_args_is_help=True)(add_ssh_key)
    ssh_app.command(name="add-identity", help="🗝️ [A] Add SSH identity (private key) to this machine")(add_ssh_identity)
    ssh_app.command(name="A", help="Add SSH identity (private key) to this machine", hidden=True)(add_ssh_identity)
    ssh_app.command(name="debug", help="🐛 [d] Debug SSH connection")(debug_ssh)
    ssh_app.command(name="d", help="Debug SSH connection", hidden=True)(debug_ssh)
    return ssh_app
