"""Wifi connect

Linux requirements:
- sudo apt-get install network-manager

Windows requirements:
- Run as Administrator for netsh commands

Configuration file format (wifi.ini):
[MyPhoneHotSpot]
SSID = MyPhoneHotSpot
pwd = mypassword123

[HomeWiFi]
SSID = HomeNetwork
pwd = homepassword456

Configuration file locations checked (in order):
- ~/dotfiles/machineconfig/setup/wifi.ini
- ~/.config/wifi.ini
- ./wifi.ini

Usage examples:
  python wifi_conn.py                     # Use default SSID from config
  python wifi_conn.py -n HomeWiFi         # Use specific configured network
  python wifi_conn.py -m                  # Manual network selection
  python wifi_conn.py -l                  # List available networks only

"""

import argparse
import configparser
from pathlib import Path
import os
import platform
import subprocess
import getpass
from typing import List, Dict, Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()


def get_available_networks() -> List[Dict[str, str]]:
    """Get list of available WiFi networks"""
    networks = []

    try:
        if platform.system() == "Windows":
            result = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output=True, text=True, check=True)

            for line in result.stdout.split("\n"):
                if "All User Profile" in line:
                    ssid = line.split(":")[1].strip()
                    networks.append({"ssid": ssid, "signal": "Unknown"})

            # Also get available networks
            result = subprocess.run(["netsh", "wlan", "show", "networks"], capture_output=True, text=True, check=True)

            current_ssid = None
            for line in result.stdout.split("\n"):
                if "SSID" in line and "BSSID" not in line:
                    current_ssid = line.split(":")[1].strip()
                elif "Signal" in line and current_ssid:
                    signal = line.split(":")[1].strip()
                    # Avoid duplicates
                    if not any(net["ssid"] == current_ssid for net in networks):
                        networks.append({"ssid": current_ssid, "signal": signal})
                    current_ssid = None

        elif platform.system() in ["Linux", "Darwin"]:
            if platform.system() == "Linux":
                result = subprocess.run(["nmcli", "-t", "-f", "SSID,SIGNAL", "device", "wifi", "list"], capture_output=True, text=True, check=True)
            else:  # Darwin/macOS - using airport command
                result = subprocess.run(["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-s"], capture_output=True, text=True, check=True)

            for line in result.stdout.strip().split("\n"):
                if line and ":" in line:
                    parts = line.split(":")
                    if len(parts) >= 2 and parts[0].strip():
                        networks.append({"ssid": parts[0].strip(), "signal": f"{parts[1].strip()}%"})

    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Error scanning networks: {e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")

    # Remove duplicates and empty SSIDs
    seen = set()
    unique_networks = []
    for net in networks:
        ssid = net["ssid"]
        if ssid and ssid not in seen:
            seen.add(ssid)
            unique_networks.append(net)

    return unique_networks


def display_and_select_network() -> Optional[Dict[str, str]]:
    """Display available networks and let user select one"""
    console.print("\n[blue]📡 Scanning for available WiFi networks...[/blue]")

    networks = get_available_networks()

    if not networks:
        console.print("[red]❌ No networks found or error occurred[/red]")
        return None

    # Display networks in a table
    table = Table(title="Available WiFi Networks")
    table.add_column("Index", style="cyan", no_wrap=True)
    table.add_column("SSID", style="green")
    table.add_column("Signal Strength", style="yellow")

    for i, network in enumerate(networks, 1):
        table.add_row(str(i), network["ssid"], network["signal"])

    console.print(table)

    # Let user select
    try:
        choice = Prompt.ask("\n[blue]Select network number (or 'q' to quit)[/blue]", default="q")

        if choice.lower() == "q":
            return None

        index = int(choice) - 1
        if 0 <= index < len(networks):
            return networks[index]
        else:
            console.print(f"[red]❌ Invalid selection. Please choose 1-{len(networks)}[/red]")
            return None

    except ValueError:
        console.print("[red]❌ Invalid input. Please enter a number.[/red]")
        return None


def connect(name: str, ssid: str):
    """Connect to a WiFi network"""
    console.print(f"\n[blue]🌐 Connecting to network: {name} (SSID: {ssid})[/blue]")

    try:
        if platform.system() == "Windows":
            subprocess.run(["netsh", "wlan", "connect", f"name={name}", f"ssid={ssid}", "interface=Wi-Fi"], capture_output=True, text=True, check=True)
        elif platform.system() == "Linux":
            subprocess.run(f"nmcli connection up '{name}'", shell=True, check=True)

        console.print("[green]✅ Connected successfully![/green]\n")

    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Error connecting: {e}[/red]")
        raise
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        raise


def connect_to_new_network(ssid: str, password: str):
    """Connect to a new network with SSID and password"""
    try:
        if platform.system() == "Windows":
            # For Windows, we create a temporary profile and connect
            create_new_connection(ssid, ssid, password)
            connect(ssid, ssid)
        elif platform.system() == "Linux":
            # For Linux, we can connect directly or create a connection
            try:
                # Try to connect directly first
                command = f"nmcli device wifi connect '{ssid}' password '{password}'"
                subprocess.run(command, shell=True, check=True)
                console.print("[green]✅ Connected successfully![/green]\n")
            except subprocess.CalledProcessError:
                # If direct connection fails, create a connection profile
                create_new_connection(ssid, ssid, password)
                connect(ssid, ssid)

    except Exception as e:
        console.print(f"[red]❌ Failed to connect to {ssid}: {e}[/red]")
        raise


def display_available_networks():
    """Display available networks (legacy function for compatibility)"""
    console.print("\n[blue]📡 Scanning for available networks...[/blue]")
    try:
        if platform.system() == "Windows":
            subprocess.run(["netsh", "wlan", "show", "networks", "interface=Wi-Fi"], check=True)
        elif platform.system() == "Linux":
            subprocess.run(["nmcli", "device", "wifi", "list"], check=True)

        console.print("[green]✅ Network scan completed![/green]\n")

    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Error scanning networks: {e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")


def try_config_connection(config_ssid: str) -> bool:
    """Try to connect using configuration file"""
    try:
        config_paths = [Path.home() / "dotfiles/machineconfig/setup/wifi.ini", Path.home() / ".config/wifi.ini", Path.cwd() / "wifi.ini"]

        creds = configparser.ConfigParser()
        config_found = False

        for config_path in config_paths:
            if config_path.exists():
                creds.read(config_path)
                config_found = True
                break

        if not config_found:
            console.print("[yellow]⚠️  No WiFi configuration file found in standard locations[/yellow]")
            return False

        if config_ssid not in creds:
            console.print(f"[yellow]⚠️  SSID '{config_ssid}' not found in configuration[/yellow]")
            available_ssids = list(creds.sections())
            if available_ssids:
                console.print(f"[blue]Available configured networks: {', '.join(available_ssids)}[/blue]")
            return False

        ssid = creds[config_ssid]["SSID"]
        password = creds[config_ssid]["pwd"]

        console.print(f"[green]✅ Found configuration for {config_ssid}[/green]")
        connect_to_new_network(ssid, password)
        return True

    except Exception as e:
        console.print(f"[red]❌ Error reading configuration: {e}[/red]")
        return False


def manual_network_selection() -> bool:
    """Manual network selection and connection"""
    network = display_and_select_network()

    if not network:
        return False

    ssid = network["ssid"]
    console.print(f"\n[blue]Selected network: {ssid}[/blue]")

    # Get password from user
    password = getpass.getpass(f"Enter password for '{ssid}': ")

    if not password:
        console.print("[red]❌ Password cannot be empty[/red]")
        return False

    try:
        connect_to_new_network(ssid, password)
        return True
    except Exception:
        return False


def main():
    """Main function with fallback network selection"""
    console.print(Panel("📶 Welcome to the WiFi Connector Tool", title="[bold blue]WiFi Connection[/bold blue]", border_style="blue"))

    parser = argparse.ArgumentParser(description="WiFi Connector")
    parser.add_argument("-n", "--ssid", help="🔗 SSID of WiFi (from config)", default="MyPhoneHotSpot")
    parser.add_argument("-m", "--manual", action="store_true", help="🔍 Manual network selection mode")
    parser.add_argument("-l", "--list", action="store_true", help="📡 List available networks only")

    args = parser.parse_args()

    # If user just wants to list networks
    if args.list:
        display_available_networks()
        return

    # If user wants manual mode, skip config and go straight to selection
    if args.manual:
        console.print("[blue]🔍 Manual network selection mode[/blue]")
        if manual_network_selection():
            console.print("[green]🎉 Successfully connected![/green]")
        else:
            console.print("[red]❌ Failed to connect[/red]")
        return

    # Try to connect using configuration first
    console.print(f"[blue]🔍 Attempting to connect to configured network: {args.ssid}[/blue]")

    if try_config_connection(args.ssid):
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


def get_current_wifi_name() -> str:
    """Get the name of the currently connected WiFi network"""
    console.print("\n[blue]🔍 Checking current WiFi connection...[/blue]")

    try:
        if platform.system() == "Windows":
            result = subprocess.run(["netsh", "wlan", "show", "interface"], capture_output=True, text=True, check=True)

            for line in result.stdout.split("\n"):
                if "SSID" in line and "BSSID" not in line:
                    wifi_name = line.split(":")[1].strip()
                    if wifi_name:
                        console.print(f"[green]✅ Connected to: {wifi_name}[/green]\n")
                        return wifi_name

            console.print("[yellow]⚠️  Not connected to WiFi[/yellow]\n")
            return "Not connected to WiFi"

        elif platform.system() == "Linux":
            result = subprocess.run(["iwgetid", "-r"], capture_output=True, text=True, check=True)

            wifi_name = result.stdout.strip()
            if wifi_name:
                console.print(f"[green]✅ Connected to: {wifi_name}[/green]\n")
                return wifi_name
            else:
                console.print("[yellow]⚠️  Not connected to WiFi[/yellow]\n")
                return "Not connected to WiFi"

    except subprocess.CalledProcessError:
        console.print("[yellow]⚠️  Not connected to WiFi or unable to detect[/yellow]\n")
        return "Not connected to WiFi"
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]\n")
        return "Error detecting WiFi"

    console.print("[yellow]⚠️  System not supported[/yellow]\n")
    return "System not supported"


def create_new_connection(name: str, ssid: str, password: str):
    """Create a new WiFi connection profile"""
    console.print(f"\n[blue]🔧 Creating new connection: {name} (SSID: {ssid})[/blue]")

    try:
        if platform.system() == "Windows":
            # Create proper Windows WiFi profile XML
            xml_config = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{name}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""

            profile_path = f"{name}.xml"
            Path(profile_path).write_text(xml_config, encoding="utf-8")

            subprocess.run(["netsh", "wlan", "add", "profile", f"filename={profile_path}", "interface=Wi-Fi"], capture_output=True, text=True, check=True)

            # Clean up the XML file
            try:
                os.remove(profile_path)
            except OSError:
                pass

        elif platform.system() == "Linux":
            # Check if connection already exists
            check_cmd = f"nmcli connection show '{name}'"
            check_result = subprocess.run(check_cmd, shell=True, capture_output=True)

            if check_result.returncode == 0:
                console.print(f"[yellow]⚠️  Connection '{name}' already exists, deleting old one...[/yellow]")
                subprocess.run(f"nmcli connection delete '{name}'", shell=True, check=True)

            command = f"nmcli connection add type wifi con-name '{name}' ssid '{ssid}' wifi-sec.key-mgmt wpa-psk wifi-sec.psk '{password}'"
            subprocess.run(command, shell=True, check=True)

        console.print("[green]✅ Connection created successfully![/green]\n")

    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Error creating connection: {e}[/red]")
        raise
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        raise


if __name__ == "__main__":
    main()
