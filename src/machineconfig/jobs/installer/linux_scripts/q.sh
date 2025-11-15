#!/bin/bash

# mkdir -p $HOME/Downloads || true
# cd $HOME/Downloads
# curl --proto '=https' --tlsv1.2 -sSf "https://desktop-release.q.us-east-1.amazonaws.com/latest/q-x86_64-linux.zip" -o "q.zip"
# unzip q.zip
# ./q/install.sh  # goes to ~/.local/bin.
# rm q.zip
# rm -rfd q

# This is a clean installation that inloves only binary movement, no bashrc manipulation.
devops install "https://desktop-release.q.us-east-1.amazonaws.com/latest/q-x86_64-linux.zip"
