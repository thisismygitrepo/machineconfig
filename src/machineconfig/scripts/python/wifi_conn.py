

import argparse
import configparser
from pathlib import Path
# import random
# import string
import os


def createNewConnection(name, SSID, password):
    config = """<?xml version=\"1.0\"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>"""+name+"""</name>
    <SSIDConfig>
        <SSID>
            <name>"""+SSID+"""</name>
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
                <keyMaterial>"""+password+"""</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""
    command = "netsh wlan add profile filename=\""+name+".xml\""+" interface=Wi-Fi"
    with open(name+".xml", 'w') as file:
        file.write(config)
    os.system(command)


def connect(name, SSID):
    command = "netsh wlan connect name=\""+name+"\" ssid=\""+SSID+"\" interface=Wi-Fi"
    os.system(command)


def displayAvailableNetworks():
    command = "netsh wlan show networks interface=Wi-Fi"
    os.system(command)


def main():
    creds = configparser.ConfigParser()
    creds.read(Path.home().joinpath('dotfiles/creds/msc/wifi.ini'))

    parser = argparse.ArgumentParser(description='Wifi Connector')
    parser.add_argument('-n', "--ssid", help=f"SSID of Wifi", default='MyPhoneHotSpot')

    args = parser.parse_args()
    ssid = creds[args.ssid]['SSID']
    pwd = creds[args.ssid]['pwd']

    # displayAvailableNetworks()
    # createNewConnection(name, name, password)
    connect(ssid, ssid)


if __name__ == '__main__':
    main()

