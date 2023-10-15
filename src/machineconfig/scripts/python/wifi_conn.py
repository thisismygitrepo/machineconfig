
"""Wifi connect
"""

import argparse
import configparser
from pathlib import Path
# import random
# import string
import os


def create_new_connection(name: str, ssid: str, password: str):
    config = """<?xml version=\"1.0\"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>""" + name + """</name>
    <SSIDConfig>
        <SSID>
            <name>""" + ssid + """</name>
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
                <keyMaterial>""" + password + """</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""
    command = "netsh wlan add profile filename=\"" + name + ".xml\"" + " interface=Wi-Fi"
    with open(name + ".xml", mode='w', encoding="utf-8") as file: file.write(config)
    os.system(command)


def connect(name: str, ssid: str):
    command = "netsh wlan connect name=\"" + name + "\" ssid=\"" + ssid + "\" interface=Wi-Fi"
    os.system(command)
def display_available_networks(): os.system("netsh wlan show networks interface=Wi-Fi")  #


def main():
    creds = configparser.ConfigParser()
    creds.read(Path.home().joinpath('dotfiles/machineconfig/setup/wifi.ini'))

    parser = argparse.ArgumentParser(description='Wifi Connector')
    parser.add_argument('-n', "--ssid", help=f"SSID of Wifi", default='MyPhoneHotSpot')

    args = parser.parse_args()
    ssid = creds[args.ssid]['SSID']
    # pwd = creds[args.ssid]['pwd']

    # displayAvailableNetworks()
    # createNewConnection(name, name, password)
    connect(ssid, ssid)


def get_current_wifi_name() -> str:
    import subprocess
    import platform
    if platform.system() == "Windows":
        try:
            cmd_output = subprocess.check_output(["netsh", "wlan", "show", "interface"], shell=True).decode("utf-8")
            wifi_name_line = [line for line in cmd_output.split("\n") if "SSID" in line][0]
            wifi_name = wifi_name_line.split(":")[1].strip()
            return wifi_name
        except Exception as e:
            print(e)
            return "Not connected to WiFi"
    elif platform.system() == "Linux":
        try:
            cmd_output = subprocess.check_output(["iwgetid", "-r"], universal_newlines=True)
            wifi_name = cmd_output.strip()
            return wifi_name
        except Exception as e:
            print(e)
            return "Not connected to WiFi"
    else: raise NotImplementedError(f"System {platform.system()} not supported.")


if __name__ == '__main__':
    main()
