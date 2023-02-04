#!/usr/bin/env bash

# as per https://www.wikihow.com/Install-Google-Chrome-Using-Terminal-on-Linux

orig_path=$(cd -- "." && pwd)

mkdir "$HOME/tmp" || exit
cd "$HOME/tmp" || exit
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install libu2f-udev  # required by chrome installer
sudo dpkg -i google-chrome-stable_current_amd64.deb
rm google-chrome-stable_current_amd64.deb
sudo apt-get install -f

cd "$orig_path" || exit
