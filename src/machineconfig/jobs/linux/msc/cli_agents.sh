#!/bin/bash


npm install -g @google/gemini-cli
npm install -g @charmland/crush
npm install -g opencode-ai@latest

curl https://cursor.com/install -fsS | bash

cd $HOME/Downloads
curl --proto '=https' --tlsv1.2 -sSf "https://desktop-release.q.us-east-1.amazonaws.com/latest/q-x86_64-linux.zip" -o "q.zip"
unzip q.zip
./q/install.sh  # goes to ~/.local/bin.
rm q.zip
rm -rfd q

