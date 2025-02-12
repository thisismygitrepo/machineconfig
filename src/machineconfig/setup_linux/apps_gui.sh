#!/bin/bash
# 🖥️ GUI Applications and Desktop Environment Setup Script

# --------------------------- libs ---------------------------------
# sudo nala install nautilus -y  # 📂 graphical file manager
# sudo nala install x11-apps  # 🎨 few graphical test apps like xeyes
sudo nala install xrdp -y  # 🔌 remote desktop protocol
#sudo nala install xorg -y  # 🎯 xorg server
#sudo nala install xinit -y  # 🚀 xorg init
#sudo nala install xserver-xorg -y  # 🖼️ xorg server
sudo nala install xfce4 -y  # 🏠 xfce4 desktop environment
sudo nala install xfce4-goodies -y  # ✨ xfce4 desktop environment extras

# --------------- 🛠️ XRDP Configuration ----------------------------------
sudo cp /etc/xrdp/xrdp.ini /etc/xrdp/xrdp.ini.bak
sudo sed -i 's/3389/3391/g' /etc/xrdp/xrdp.ini  # 🔄 change port to avoid Windows collision

# 🎨 Controls screen scaling and color:
sudo sed -i 's/max_bpp=32/#max_bpp=32\nmax_bpp=128/g' /etc/xrdp/xrdp.ini
sudo sed -i 's/xserverbpp=24/#xserverbpp=24\nxserverbpp=128/g' /etc/xrdp/xrdp.ini
echo xfce4-session > ~/.xsession

# 🔧 Configure startup
sudo sed -i 's/test/#test/g' /etc/xrdp/startwm.sh
sudo sed -i 's/exec/#exec/g' /etc/xrdp/startwm.sh
echo "startxfce4" | sudo tee /etc/xrdp/startwm.sh

# 🚀 Start XRDP service
sudo /etc/init.d/xrdp start
# Alternative commands:
# sudo systemctl restart xrdp
# sudo service xrdp restart

