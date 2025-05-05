#!/bin/bash
#=======================================================================
# 💻 LAPTOP LID CONFIGURATION 🔌
#=======================================================================
# This script disables suspension when laptop lid is closed
# Reference: https://askubuntu.com/questions/141866/keep-ubuntu-server-running-on-a-laptop-with-the-lid-closed/1426611#1426611

echo """#=======================================================================
🔧 CONFIGURING | Modifying lid close behavior
#=======================================================================
"""

# Edit file: /etc/systemd/logind.conf and adjust lid handling parameters
echo "📝 Updating HandleLidSwitch parameter..."
sudo sed -i 's/#HandleLidSwitch=suspend/HandleLidSwitch=ignore/g' /etc/systemd/logind.conf

echo "📝 Updating HandleLidSwitchExternalPower parameter..."
sudo sed -i 's/#HandleLidSwitchExternalPower=suspend/HandleLidSwitchExternalPower=ignore/g' /etc/systemd/logind.conf

echo """#=======================================================================
✅ COMPLETE | Lid close configuration has been updated
#=======================================================================
"""
echo "ℹ️ You may need to restart the systemd-logind service or reboot for changes to take effect"
