
import machineconfig.scripts.python.helpers_devops.cli_share_file
import machineconfig.scripts.python.helpers_devops.cli_share_terminal as cli_share_terminal
import machineconfig.scripts.python.helpers_devops.cli_share_server as cli_share_server
import typer
from typing import Optional, Annotated



def install_ssh_server():
    """📡 SSH install server"""
    import platform
    if platform.system() == "Windows":
        from machineconfig.setup_windows import SSH_SERVER
    elif platform.system() == "Linux" or platform.system() == "Darwin":
        from machineconfig.setup_linux import SSH_SERVER
    else:
        raise NotImplementedError(f"Platform {platform.system()} is not supported.")
    from machineconfig.utils.code import run_shell_script
    run_shell_script(script=SSH_SERVER.read_text(encoding="utf-8"))


def add_ssh_key(path: Annotated[Optional[str], typer.Option(..., help="Path to the public key file")] = None,
         choose: Annotated[bool, typer.Option(..., "--choose", "-c", help="Choose from available public keys in ~/.ssh/*.pub")] = False,
         value: Annotated[bool, typer.Option(..., "--value", "-v", help="Paste the public key content manually")] = False,
         github: Annotated[Optional[str], typer.Option(..., "--github", "-g", help="Fetch public keys from a GitHub username")] = None
):
    """🔑 SSH add pub key to this machine so its accessible by owner of corresponding private key."""
    import machineconfig.scripts.python.helpers_network.devops_add_ssh_key as helper
    helper.main(pub_path=path, pub_choose=choose, pub_val=value, from_github=github)
def add_ssh_identity():
    """🗝️ SSH add identity (private key) to this machine"""
    import machineconfig.scripts.python.helpers_network.devops_add_identity as helper
    helper.main()


def show_address() -> None:
    """📌 Show this computer addresses on network"""
    from machineconfig.utils.installer_utils.installer_cli import install_if_missing
    import subprocess
    install_if_missing("ipinfo")
    result = subprocess.run(
        ["ipinfo", "myip", "--json"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    import json
    loaded_json = json.loads(result.stdout)
    from rich import print_json
    print_json(data=loaded_json)

    import machineconfig.scripts.python.helpers_network.address as helper
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


def debug_ssh():
    """🐛 SSH debug"""
    from platform import system
    if system() == "Linux" or system() == "Darwin":
        import machineconfig.scripts.python.helpers_network.ssh_debug_linux as helper
        helper.ssh_debug_linux()
    elif system() == "Windows":
        import machineconfig.scripts.python.helpers_network.ssh_debug_windows as helper
        helper.ssh_debug_windows()
    else:
        raise NotImplementedError(f"Platform {system()} is not supported.")

def wifi_select(
    ssid: Annotated[str, typer.Option("-n", "--ssid", help="🔗 SSID of WiFi (from config)")] = "MyPhoneHotSpot",
    manual: Annotated[bool, typer.Option("-m", "--manual", help="🔍 Manual network selection mode")] = False,
    list_: Annotated[bool, typer.Option("-l", "--list", help="📡 List available networks only")] = False,
) -> None:
    """Main function with fallback network selection"""
    from rich.panel import Panel
    from rich.prompt import Confirm
    from rich.console import Console
    from machineconfig.scripts.python.helpers_network.wifi_conn import try_config_connection, manual_network_selection, display_available_networks
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



def reset_cloudflare_tunnel():
    code = """
# cloudflared tunnel route dns glenn  # creates CNAMES in Cloudflare dashboard
# sudo systemctl stop cloudflared
# test: cloudflared tunnel run glenn
home_dir=$HOME
cloudflared_path="$home_dir/.local/bin/cloudflared"
sudo $cloudflared_path service uninstall
sudo rm /etc/cloudflared/config.yml || true
sudo $cloudflared_path --config $home_dir/.cloudflared/config.yml service install
"""
    print(code)
def add_ip_exclusion_to_warp(ip: Annotated[str, typer.Option(..., "--ip", help="IP address to exclude from WARP")]):
    code = f"""
sudo warp-cli tunnel ip add {ip}
sudo warp-cli disconnect
sudo warp-cli connect
"""
    print(code)


def get_app():
    nw_apps = typer.Typer(help="🔐 [n] Network subcommands", no_args_is_help=True, add_help_option=False, add_completion=False)
    nw_apps.command(name="share-terminal", help="📡  [t] Share terminal via web browser")(cli_share_terminal.share_terminal)
    nw_apps.command(name="t", help="Share terminal via web browser", hidden=True)(cli_share_terminal.share_terminal)

    nw_apps.command(name="share-server", help="🌐  [s] Start local/global server to share files/folders via web browser", no_args_is_help=True)(cli_share_server.web_file_explorer)
    nw_apps.command(name="s", help="Start local/global server to share files/folders via web browser", hidden=True, no_args_is_help=True)(cli_share_server.web_file_explorer)

    # app = cli_share_server.get_share_file_app()
    # nw_apps.add_typer(app, name="share-file", help="📁  [f] Share a file via relay server", no_args_is_help=True)
    # nw_apps.add_typer(app, name="f", help="Share a file via relay server", hidden=True, no_args_is_help=True)
    nw_apps.command(name="send", no_args_is_help=True, hidden=False, help="📁 [sx] send files from here.")(machineconfig.scripts.python.helpers_devops.cli_share_file.share_file_send)
    nw_apps.command(name="sx", no_args_is_help=True, hidden=True, help="📁 [sx] send files from here.")(machineconfig.scripts.python.helpers_devops.cli_share_file.share_file_send)
    nw_apps.command(name="receive", no_args_is_help=True, hidden=False, help="📁 [rx] receive files to here.")(machineconfig.scripts.python.helpers_devops.cli_share_file.share_file_receive)
    nw_apps.command(name="rx", no_args_is_help=True, hidden=True, help="📁 [rx] receive files to here.")(machineconfig.scripts.python.helpers_devops.cli_share_file.share_file_receive)

    nw_apps.command(name="install-ssh-server", help="📡  [i] Install SSH server")(install_ssh_server)
    nw_apps.command(name="i", help="Install SSH server", hidden=True)(install_ssh_server)
    nw_apps.command(name="add-ssh-key", help="🔑  [k] Add SSH public key to this machine", no_args_is_help=True)(add_ssh_key)
    nw_apps.command(name="k", help="Add SSH public key to this machine", hidden=True, no_args_is_help=True)(add_ssh_key)
    nw_apps.command(name="add-ssh-identity", help="🗝️  [A] Add SSH identity (private key) to this machine")(add_ssh_identity)
    nw_apps.command(name="A", help="Add SSH identity (private key) to this machine", hidden=True)(add_ssh_identity)
    nw_apps.command(name="show-address", help="📌  [a] Show this computer addresses on network")(show_address)
    nw_apps.command(name="a", help="Show this computer addresses on network", hidden=True)(show_address)
    nw_apps.command(name="debug-ssh", help="🐛  [d] Debug SSH connection")(debug_ssh)
    nw_apps.command(name="d", help="Debug SSH connection", hidden=True)(debug_ssh)

    nw_apps.command(name="wifi-select", no_args_is_help=True, help="📶  [w] WiFi connection utility.")(wifi_select)
    nw_apps.command(name="w", no_args_is_help=True, hidden=True)(wifi_select)

    nw_apps.command(name="bind-wsl-port", help="🔌  [b] Bind WSL port to Windows host", no_args_is_help=True)(bind_wsl_port)
    nw_apps.command(name="b", help="Bind WSL port to Windows host", hidden=True, no_args_is_help=True)(bind_wsl_port)

    nw_apps.command(name="reset-cloudflare-tunnel", help="☁️  [r] Reset Cloudflare tunnel service")(reset_cloudflare_tunnel)
    nw_apps.command(name="r", help="Reset Cloudflare tunnel service", hidden=True)(reset_cloudflare_tunnel)
    nw_apps.command(name="add-ip-exclusion-to-warp", help="🚫  [p] Add IP exclusion to WARP")(add_ip_exclusion_to_warp)
    nw_apps.command(name="p", help="Add IP exclusion to WARP", hidden=True)(add_ip_exclusion_to_warp)

    return nw_apps
