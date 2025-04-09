"""Wifi connect

sudo apt-get install network-manager

"""

import argparse
import configparser
from pathlib import Path
import os
import platform
import subprocess

def create_new_connection(name: str, ssid: str, password: str):
    print(f"\n🔧 Creating new connection: {name} (SSID: {ssid})")
    if platform.system() == "Windows":
        config = """<?xml version=\"1.0\"?>
        // ...existing XML config...
        """
        command = "netsh wlan add profile filename=\"" + name + ".xml\"" + " interface=Wi-Fi"
        with open(name + ".xml", mode='w', encoding="utf-8") as file:
            file.write(config)
        os.system(command)
    elif platform.system() == "Linux":
        command = f"nmcli connection add type wifi con-name '{name}' ssid '{ssid}' wifi-sec.key-mgmt wpa-psk wifi-sec.psk '{password}'"
        subprocess.run(command, shell=True, check=True)
    print("✅ Connection created successfully!\n")

def connect(name: str, ssid: str):
    print(f"\n🌐 Connecting to network: {name} (SSID: {ssid})")
    if platform.system() == "Windows":
        command = "netsh wlan connect name=\"" + name + "\" ssid=\"" + ssid + "\" interface=Wi-Fi"
        os.system(command)
    elif platform.system() == "Linux":
        command = f"nmcli connection up '{name}'"
        subprocess.run(command, shell=True, check=True)
    print("✅ Connected successfully!\n")

def display_available_networks():
    print("\n📡 Scanning for available networks...")
    if platform.system() == "Windows":
        os.system("netsh wlan show networks interface=Wi-Fi")
    elif platform.system() == "Linux":
        subprocess.run("nmcli device wifi list", shell=True, check=True)
    print("✅ Network scan completed!\n")

def main():
    print("\n" + "=" * 50)
    print("📶 Welcome to the WiFi Connector Tool")
    print("=" * 50 + "\n")

    creds = configparser.ConfigParser()
    creds.read(Path.home().joinpath('dotfiles/machineconfig/setup/wifi.ini'))

    parser = argparse.ArgumentParser(description='WiFi Connector')
    parser.add_argument('-n', "--ssid", help="🔗 SSID of WiFi", default='MyPhoneHotSpot')

    args = parser.parse_args()
    ssid = creds[args.ssid]['SSID']
    password = creds[args.ssid]['pwd']

    create_new_connection(ssid, ssid, password)
    connect(ssid, ssid)

def get_current_wifi_name() -> str:
    print("\n🔍 Checking current WiFi connection...")
    if platform.system() == "Windows":
        try:
            cmd_output = subprocess.check_output(["netsh", "wlan", "show", "interface"], shell=True).decode("utf-8")
            wifi_name_line = [line for line in cmd_output.split("\n") if "SSID" in line][0]
            wifi_name = wifi_name_line.split(":")[1].strip()
            print(f"✅ Connected to: {wifi_name}\n")
            return wifi_name
        except Exception as e:
            print(f"❌ Error: {e}\n")
            return "Not connected to WiFi"
    elif platform.system() == "Linux":
        try:
            cmd_output = subprocess.check_output(["iwgetid", "-r"], universal_newlines=True)
            wifi_name = cmd_output.strip()
            print(f"✅ Connected to: {wifi_name}\n")
            return wifi_name
        except Exception as e:
            print(f"❌ Error: {e}\n")
            return "Not connected to WiFi"
    else:
        raise NotImplementedError(f"❌ System {platform.system()} not supported.")

if __name__ == '__main__':
    main()
