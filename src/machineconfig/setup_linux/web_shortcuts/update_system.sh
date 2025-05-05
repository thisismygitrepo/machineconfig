#!/usr/bin/bash
#=======================================================================
# 🔄 SYSTEM UPDATE SCRIPT
#=======================================================================
# This script provides methods to update Ubuntu system and kernel

echo """#=======================================================================
🔄 SYSTEM UPGRADE OPTIONS | Ubuntu system maintenance
#=======================================================================
"""

echo """#=======================================================================
📦 UBUNTU DISTRIBUTION UPGRADE | Full system version upgrade
#=======================================================================

⚠️  This will upgrade Ubuntu to the next available release
    Edit /etc/update-manager/release-upgrades to configure upgrade behavior
"""
# Uncomment the line below to actually run the upgrade
# do-release-upgrade 

echo """#=======================================================================
🔧 KERNEL UPDATE | Installing the latest Linux kernel
#=======================================================================

📥 Downloading Ubuntu mainline kernel installation script...
"""
wget https://raw.githubusercontent.com/pimlie/ubuntu-mainline-kernel.sh/master/ubuntu-mainline-kernel.sh

echo """🛠️  Installing script to system path...
"""
sudo install ubuntu-mainline-kernel.sh /usr/local/bin/

echo """🔍 Checking available kernel versions...
"""
sudo ubuntu-mainline-kernel.sh -c

echo """⏳ Installing the latest kernel (this may take several minutes)...
"""
sudo ubuntu-mainline-kernel.sh -i -y

echo """#=======================================================================
✅ UPDATE COMPLETE | System upgrade finished
#=======================================================================

⚠️  IMPORTANT: A system reboot is required to use the new kernel
    To reboot now, run: sudo reboot
"""
