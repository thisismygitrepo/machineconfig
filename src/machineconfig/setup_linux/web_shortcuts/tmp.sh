curl -O http://ftp.debian.org/debian/pool/main/d/debootstrap/debootstrap_1.0.141_all.deb
ar x debootstrap_1.0.141_all.deb
tar -xf data.tar.xz
sudo cp -a usr/share/debootstrap /usr/share/
sudo cp usr/sbin/debootstrap /usr/sbin/
