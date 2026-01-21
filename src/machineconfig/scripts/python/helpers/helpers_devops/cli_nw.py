
import machineconfig.scripts.python.helpers.helpers_devops.cli_share_file
import machineconfig.scripts.python.helpers.helpers_devops.cli_share_terminal as cli_share_terminal
import machineconfig.scripts.python.helpers.helpers_devops.cli_share_server as cli_share_server
import machineconfig.scripts.python.helpers.helpers_devops.cli_ssh as cli_ssh
import machineconfig.scripts.python.helpers.helpers_devops.cli_share_temp as cli_share_temp
import typer
from typing import Annotated, Literal


def switch_public_ip_address(
    wait_seconds: Annotated[float, typer.Option(..., "--wait", "-w", help="Seconds to wait between steps")] = 2.0,
    max_trials: Annotated[int, typer.Option(..., "--max-trials", "-m", help="Max number of switch attempts")] = 10,
) -> None:
    """🔁 Switch public IP address (Cloudflare WARP)"""
    import machineconfig.scripts.python.helpers.helpers_network.address_switch as helper
    helper.switch_public_ip_address(max_trials=max_trials, wait_seconds=wait_seconds)


def show_address() -> None:
    """📌 Show this computer addresses on network"""
    import machineconfig.scripts.python.helpers.helpers_network.address as helper

    try:
        loaded_json = helper.get_public_ip_address()
        from rich import print_json
        print_json(data=loaded_json)
    except Exception as e:
        print(f"⚠️  Could not fetch public IP address: {e}")
        loaded_json = {}

    from rich.table import Table
    from rich.console import Console
    res = helper.get_all_ipv4_addresses()
    res.append( ("Public IP", loaded_json.get("ip", "N/A")))
    
    # loc = loaded_json["loc"]
    # cmd = f"""curl "https://maps.geoapify.com/v1/staticmap?style=osm-bright&width=600&height=300&center=lonlat:{loc}&zoom=6&marker=lonlat:{loc};color:%23ff0000;size:medium&apiKey=$GEOAPIFY_API_KEY" -o map.png && chafa map.png"""
    # from machineconfig.utils.code import run_shell_script
    # run_shell_script(script=cmd)

    table = Table(title="Network Interfaces")
    table.add_column("Interface", style="cyan")
    table.add_column("IP Address", style="green")
    
    for iface, ip in res:
        table.add_row(iface, ip)
    
    console = Console()
    console.print(table)
    
    res = helper.select_lan_ipv4(prefer_vpn=False)
    if res is not None:
        # ip, iface = res
        # print(f"Selected IP: {ip} on interface: {iface}")
        print(f"LAN IPv4: {res}")
    else:
        print("No network interfaces found.")



def bind_wsl_port(port: Annotated[int, typer.Option(..., "--port", "-p", help="Port number to bind")]):
    code = f"""

$wsl_ip = (wsl.exe hostname -I).Trim().Split(' ')[0]
netsh interface portproxy add v4tov4 listenport={port} listenaddress=0.0.0.0 connectport={port} connectaddress=$wsl_ip

"""
    from machineconfig.utils.code import exit_then_run_shell_script
    exit_then_run_shell_script(code)
def open_wsl_port(ports: Annotated[str, typer.Argument(..., help="Comma-separated ports or port ranges (e.g., '8080,3000-3005,443')")]):
    """🔥 Open Windows firewall ports for WSL (Windows only)."""
    import machineconfig.utils.ssh_utils.wsl as wsl_utils
    wsl_utils.open_wsl_port(ports)
def link_wsl_and_windows_home(windows_username: Annotated[str | None, typer.Option("--windows-username", "-u", help="Windows username to use (optional, auto-detected if not provided)")] = None):
    """🔗 Link WSL home and Windows home directories."""
    import machineconfig.utils.ssh_utils.wsl as wsl_utils
    wsl_utils.link_wsl_and_windows(windows_username)


def wifi_select(
    ssid: Annotated[str, typer.Option("-n", "--ssid", help="🔗 SSID of WiFi (from config)")] = "MyPhoneHotSpot",
    manual: Annotated[bool, typer.Option("-m", "--manual", help="🔍 Manual network selection mode")] = False,
    list_: Annotated[bool, typer.Option("-l", "--list", help="📡 List available networks only")] = False,
) -> None:
    """Main function with fallback network selection"""
    from rich.panel import Panel
    from rich.prompt import Confirm
    from rich.console import Console
    from machineconfig.scripts.python.helpers.helpers_network.wifi_conn import try_config_connection, manual_network_selection, display_available_networks
    console = Console()
    console.print(Panel("📶 Welcome to the WiFi Connector Tool", title="[bold blue]WiFi Connection[/bold blue]", border_style="blue"))

    # If user just wants to list networks
    if list_:
        display_available_networks()
        return

    # If user wants manual mode, skip config and go straight to selection
    if manual:
        console.print("[blue]🔍 Manual network selection mode[/blue]")
        if manual_network_selection():
            console.print("[green]🎉 Successfully connected![/green]")
        else:
            console.print("[red]❌ Failed to connect[/red]")
        return

    # Try to connect using configuration first
    console.print(f"[blue]🔍 Attempting to connect to configured network: {ssid}[/blue]")

    if try_config_connection(ssid):
        console.print("[green]🎉 Successfully connected using configuration![/green]")
        return

    # Configuration failed, offer fallback options
    console.print("\n[yellow]⚠️  Configuration connection failed or not available[/yellow]")

    if Confirm.ask("[blue]Would you like to manually select a network?[/blue]", default=True):
        if manual_network_selection():
            console.print("[green]🎉 Successfully connected![/green]")
        else:
            console.print("[red]❌ Failed to connect[/red]")
    else:
        console.print("[blue]👋 Goodbye![/blue]")



def reset_cloudflare_tunnel(task: Annotated[Literal["oneoff-shell-process", "oneoff-background-process", "as-service"], typer.Option(..., "--task", "-t", help="Task to perform", case_sensitive=False, show_choices=True)],
                            tunnel_name: Annotated[str | None, typer.Option("--tunnel-name", "-n", help="Name of the Cloudflare tunnel to run")] = None,
                    ):
    code = """
# cloudflared tunnel route dns glenn  # creates CNAMES in Cloudflare dashboard
# sudo systemctl stop cloudflared
"""
    match task:
        case "oneoff-shell-process":
            if tunnel_name is None: tunnel_name = ""
            code = f"""cloudflared tunnel run {tunnel_name}  #  This is running like a normal command """
        case "oneoff-background-process":
            if tunnel_name is None: tunnel_name = ""
            import getpass
            user_name = getpass.getuser()
            code = f"""
# This verion runs like a deamon, but its not peristent across reboots
sudo systemd-run \
  --unit=cloudflared-tunnel \
  --description="Cloudflared Tunnel (transient)" \
  --property=Restart=on-failure \
  --property=RestartSec=5 \
  --property=User={user_name} \
  --property=Group={user_name} \
  --property=Environment=HOME=/home/{user_name} \
  --property=WorkingDirectory=/home/{user_name} \
  /home/{user_name}/.local/bin/cloudflared \
    --config /home/{user_name}/.cloudflared/config.yml \
    tunnel run {tunnel_name}
"""
        case "as-service":
            code = """
home_dir=$HOME
cloudflared_path="$home_dir/.local/bin/cloudflared"
sudo $cloudflared_path service uninstall
sudo rm /etc/cloudflared/config.yml || true
sudo $cloudflared_path --config $home_dir/.cloudflared/config.yml service install
"""


    from machineconfig.utils.code import exit_then_run_shell_script, print_code
    print_code(code, lexer="bash", desc="code to achieve the goal")
    yes = typer.confirm("Do you want to run the above commands now?", default=False)
    if yes:
        exit_then_run_shell_script(code)
    


def vscode_share(
    action: Annotated[Literal["run", "install-service", "uninstall-service", "share-local"], typer.Option(..., "--action", "-a", help="Action to perform", case_sensitive=False, show_choices=True)],
    name: Annotated[str | None, typer.Option("--name", "-n", help="Name for the tunnel/service")] = None,
    path: Annotated[str | None, typer.Option("--path", "-p", help="Path to share locally (for share-local)")] = None,
    extra_args: Annotated[str | None, typer.Option("--extra-args", "-e", help="Extra args to append to the code tunnel command")] = None,
) -> None:
    """🧑‍💻 Share workspace using VS Code Tunnels ("code tunnel")

    Note: this helper prints recommended commands and optionally runs them.
    If you need more functionality, consult VS Code Tunnels docs: https://code.visualstudio.com/docs/remote/tunnels
    """
    accept = "--accept-server-license-terms"
    name_part = f"--name {name}" if name else ""
    extra = extra_args or ""

    if action == "run":
        cmd = f"code tunnel {name_part} {accept} {extra}".strip()
        desc = "Run a one-off VS Code tunnel (foreground)"
    elif action == "install-service":
        cmd = f"code tunnel service install {accept} {name_part}".strip()
        desc = "Install code tunnel as a service"
    elif action == "uninstall-service":
        cmd = "code tunnel service uninstall"
        desc = "Uninstall code tunnel service"
    elif action == "share-local":
        p = path or "."
        # Some VS Code CLI integrations prefer starting a tunnel and then using the editor to expose resources.
        cmd = f"code tunnel {name_part} {accept} {extra}".strip()
        desc = f"Start tunnel and then share local path: {p} (use VS Code UI to forward ports / share files)"
    else:
        print(f"Unknown action: {action}")
        return

    from machineconfig.utils.code import print_code, exit_then_run_shell_script
    print_code(cmd, lexer="bash", desc=desc)

    if typer.confirm("Do you want to run the above command now?", default=False):
        exit_then_run_shell_script(cmd)
    else:
        print("Command not executed. Use the printed command in your terminal when ready.")
    


def add_ip_exclusion_to_warp(ip: Annotated[str, typer.Option(..., "--ip", help="IP address(es) to exclude from WARP (Comma separated)")]):
    ips = ip.split(",")
    res = ""
    for an_ip in ips:
        res += f'sudo warp-cli tunnel ip add {an_ip}\n'
        print(f"Adding IP exclusion to WARP for: {an_ip}")
    code = f"""
{res}
echo "Restarting WARP connection..."
sudo warp-cli disconnect
echo "Waiting for 2 seconds..."
sleep 2
echo "Reconnecting WARP..."
sudo warp-cli connect
"""
    print(code)
    print("NOTE: Please run the above commands in your terminal to apply the changes.")


def get_app():
    nw_apps = typer.Typer(help="🔐 [n] Network subcommands", no_args_is_help=True, add_help_option=True, add_completion=False)
    nw_apps.command(name="share-terminal", help="📡 [t] Share terminal via web browser")(cli_share_terminal.share_terminal)
    nw_apps.command(name="t", help="Share terminal via web browser", hidden=True)(cli_share_terminal.share_terminal)

    nw_apps.command(name="share-server", help="🌐 [s] Start local/global server to share files/folders via web browser", no_args_is_help=True)(cli_share_server.web_file_explorer)
    nw_apps.command(name="s", help="Start local/global server to share files/folders via web browser", hidden=True, no_args_is_help=True)(cli_share_server.web_file_explorer)

    # app = cli_share_server.get_share_file_app()
    # nw_apps.add_typer(app, name="share-file", help="📁 [f] Share a file via relay server", no_args_is_help=True)
    # nw_apps.add_typer(app, name="f", help="Share a file via relay server", hidden=True, no_args_is_help=True)
    nw_apps.command(name="send", no_args_is_help=True, hidden=False, help="📁 [sx] send files from here.")(machineconfig.scripts.python.helpers.helpers_devops.cli_share_file.share_file_send)
    nw_apps.command(name="sx", no_args_is_help=True, hidden=True, help="📁 [sx] send files from here.")(machineconfig.scripts.python.helpers.helpers_devops.cli_share_file.share_file_send)
    nw_apps.command(name="receive", no_args_is_help=True, hidden=False, help="📁 [rx] receive files to here.")(machineconfig.scripts.python.helpers.helpers_devops.cli_share_file.share_file_receive)
    nw_apps.command(name="rx", no_args_is_help=True, hidden=True, help="📁 [rx] receive files to here.")(machineconfig.scripts.python.helpers.helpers_devops.cli_share_file.share_file_receive)

    nw_apps.command(name="share-temp-file", help="🌡️ [T] Share a file via temp.sh")(cli_share_temp.upload_file)
    nw_apps.command(name="T", help="Share a file via temp.sh", hidden=True)(cli_share_temp.upload_file)

    nw_apps.add_typer(cli_ssh.get_app(), name="ssh", help="🔐 [S] SSH subcommands")
    nw_apps.add_typer(cli_ssh.get_app(), name="S", help="SSH subcommands", hidden=True)

    nw_apps.command(name="show-address", help="📌 [a] Show this computer addresses on network")(show_address)
    nw_apps.command(name="a", help="Show this computer addresses on network", hidden=True)(show_address)

    nw_apps.command(name="switch-public-ip", help="🔁 [c] Switch public IP address (Cloudflare WARP)")(switch_public_ip_address)
    nw_apps.command(name="c", help="Switch public IP address (Cloudflare WARP)", hidden=True)(switch_public_ip_address)

    nw_apps.command(name="wifi-select", no_args_is_help=True, help="📶 [w] WiFi connection utility.")(wifi_select)
    nw_apps.command(name="w", no_args_is_help=True, hidden=True)(wifi_select)

    nw_apps.command(name="bind-wsl-port", help="🔌 [b] Bind WSL port to Windows host", no_args_is_help=True)(bind_wsl_port)
    nw_apps.command(name="b", help="Bind WSL port to Windows host", hidden=True, no_args_is_help=True)(bind_wsl_port)
    nw_apps.command(name="open-wsl-port", no_args_is_help=True, help="🔥 [o] Open Windows firewall ports for WSL.", hidden=False)(open_wsl_port)
    nw_apps.command(name="o", no_args_is_help=True, help="Open Windows firewall ports for WSL.", hidden=True)(open_wsl_port)
    nw_apps.command(name="link-wsl-windows", no_args_is_help=False, help="🔗 [l] Link WSL home and Windows home directories.", hidden=False)(link_wsl_and_windows_home)
    nw_apps.command(name="l", no_args_is_help=False, help="Link WSL home and Windows home directories.", hidden=True)(link_wsl_and_windows_home)


    nw_apps.command(name="reset-cloudflare-tunnel", help="☁️ [r] Reset Cloudflare tunnel service")(reset_cloudflare_tunnel)
    nw_apps.command(name="r", help="Reset Cloudflare tunnel service", hidden=True)(reset_cloudflare_tunnel)
    nw_apps.command(name="add-ip-exclusion-to-warp", help="🚫 [p] Add IP exclusion to WARP")(add_ip_exclusion_to_warp)
    nw_apps.command(name="p", help="Add IP exclusion to WARP", hidden=True)(add_ip_exclusion_to_warp)

    # VS Code Tunnels helper
    nw_apps.command(name="vscode-share", no_args_is_help=True, help="🧑‍💻 [v] Share workspace via VS Code Tunnels")(vscode_share)
    nw_apps.command(name="v", no_args_is_help=True, hidden=True, help="Share workspace via VS Code Tunnels")(vscode_share)

    return nw_apps
