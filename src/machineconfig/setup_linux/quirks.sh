

# to disable suspension with lid closing: https://askubuntu.com/questions/141866/keep-ubuntu-server-running-on-a-laptop-with-the-lid-closed/1426611#1426611?newreg=b07cf38c193d4abd97bd9c05f3ace8d2
# Edit file: /etc/systemd/logind.conf Adjust these two parameters:
sed -i 's/HandleLidSwitch=suspend/HandleLidSwitch=ignore/g' /etc/systemd/logind.conf
sed -i 's/HandleLidSwitchExternalPower=suspend/HandleLidSwitchExternalPower=ignore/g' /etc/systemd/logind.conf

# https://askubuntu.com/questions/972215/a-start-job-is-running-for-wait-for-network-to-be-configured-ubuntu-server-17-1
# This is the network config written by 'subiquity'

network:
  ethernets:
    enp0s31f6:
      dhcp4: true
      optional: true
  version: 2


sed -i 's/dhcp4: true/dhcp4: false/g' /etc/netplan/01-netcfg.yaml

# see sed and awk
# https://unix.stackexchange.com/questions/642578/command-line-for-editing-a-configuration-file-value-without-an-interactive-edito
