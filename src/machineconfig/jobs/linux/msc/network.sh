#!/bin/bash
#=======================================================================
# 🌐 NETWORK CONFIGURATION SCRIPT 🌐
#=======================================================================
# This script fixes the "A start job is running for wait for network to be configured" issue
# Reference: https://askubuntu.com/questions/972215/a-start-job-is-running-for-wait-for-network-to-be-configured-ubuntu-server-17-1

echo """#=======================================================================
🔧 CONFIGURING NETWORK | Making network interfaces optional
#=======================================================================
"""

echo "📋 Original network config format from 'subiquity':"
echo """# network:
#   ethernets:
#     enp0s31f6:
#       dhcp4: true
#       optional: true
#   version: 2
"""

echo "🔄 Modifying netplan configuration..."
sudo sed -i 's/dhcp4: true/dhcp4: true\n      optional: true/g' /etc/netplan/00-installer-config.yaml

echo """#=======================================================================
✅ COMPLETE | Network configuration has been updated
#=======================================================================
"""
echo "ℹ️ You may need to run 'sudo netplan apply' for changes to take effect"

# Additional references:
# - sed/awk editing: https://unix.stackexchange.com/questions/642578/command-line-for-editing-a-configuration-file-value-without-an-interactive-edito
# - shell script file format: https://askubuntu.com/questions/304999/not-able-to-execute-a-sh-file-bin-bashm-bad-interpreter
# - plocate: https://unix.stackexchange.com/questions/113670/can-i-just-disable-updatedb/113681#113681
# - mlocate performance: https://askubuntu.com/questions/1251484/why-does-it-take-so-much-time-to-initialize-mlocate-database

