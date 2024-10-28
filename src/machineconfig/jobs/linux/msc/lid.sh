

# to disable suspension with lid closing: https://askubuntu.com/questions/141866/keep-ubuntu-server-running-on-a-laptop-with-the-lid-closed/1426611#1426611?newreg=b07cf38c193d4abd97bd9c05f3ace8d2
# Edit file: /etc/systemd/logind.conf Adjust these two parameters:
sudo sed -i 's/#HandleLidSwitch=suspend/HandleLidSwitch=ignore/g' /etc/systemd/logind.conf
sudo sed -i 's/#HandleLidSwitchExternalPower=suspend/HandleLidSwitchExternalPower=ignore/g' /etc/systemd/logind.conf
