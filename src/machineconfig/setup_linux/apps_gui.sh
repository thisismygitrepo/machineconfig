
# --------------------------- libs ---------------------------------
# sudo apt install nautilus -y  # graphical file manager
# sudo apt install x11-apps  # few graphical test apps like xeyes
sudo apt install xrdp -y  # remote desktop protocol
#sudo apt install xorg -y  # xorg server
#sudo apt install xinit -y  # xorg init
#sudo apt install xserver-xorg -y  # xorg server

sudo apt install xfce4 -y  # xfce4 desktop environment
sudo apt install xfce4-goodies -y  # xfce4 desktop environment

# --------------- setup ----------------------------------
sudo cp /etc/xrdp/xrdp.ini /etc/xrdp/xrdp.ini.bak
sudo sed -i 's/3389/3391/g' /etc/xrdp/xrdp.ini  # change port to 3390, cause we don't want collission with windows
# Controls screen scaling and color:
sudo sed -i 's/max_bpp=32/#max_bpp=32\nmax_bpp=128/g' /etc/xrdp/xrdp.ini
sudo sed -i 's/xserverbpp=24/#xserverbpp=24\nxserverbpp=128/g' /etc/xrdp/xrdp.ini

echo xfce4-session > ~/.xsession
# add gnome to .xsession

sudo sed -i 's/test/#test/g' /etc/xrdp/startwm.sh  # comment out test line in /etc/xrdp/startwm.sh
sudo sed -i 's/exec/#exec/g' /etc/xrdp/startwm.sh  # comment out exec line in /etc/xrdp/startwm.sh

# startxfce4 >> /etc/xrdp/startwm.sh  # add startxfce4 as newline to /etc/xrdp/startwm.sh
# or use tee with sudo to add that line:
echo "startxfce4" | sudo tee /etc/xrdp/startwm.sh

#gnome-session >> /etc/xrdp/startwm.sh  # add gnome desktop enviroment as newline to /etc/xrdp/startwm.sh


sudo /etc/init.d/xrdp start
# sudo systemctl restart xrdp
# alternative if systemctl is not available:
# sudo service xrdp restart

