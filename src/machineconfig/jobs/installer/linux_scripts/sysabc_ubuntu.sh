sudo apt update -y || true
sudo apt install nala -y || true
sudo nala install curl wget gpg lsb-release apt-transport-https \
  samba fuse3 nfs-common \
  git net-tools htop nano \
  build-essential \  # Where it brings gcc, make, etc.,
  python3-dev \  # ensures headers for your Python version.
  unzip \   # bun installer needs this to unzip files.
  pkg-config \  
  libssl-dev \  # essential for SSL/TLS support in many applications, compiling rust binaries will need them.
    -y || true

curl -fsSL https://bun.com/install | bash
. ~/.bashrc || true
sudo ln -s ~/.bun/bin/bun /usr/local/bin/node  # trick programs that expect node to use bun runtime.

# echo 'keyboard-configuration keyboard-configuration/layout select US English' | sudo debconf-set-selections
# echo 'keyboard-configuration keyboard-configuration/layoutcode string us' | sudo debconf-set-selections
# sudo DEBIAN_FRONTEND=noninteractive nala install cmatrix hollywood ffmpeg -y  make || true
