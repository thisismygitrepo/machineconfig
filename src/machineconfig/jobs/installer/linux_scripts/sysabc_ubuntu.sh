sudo apt update -y || true
sudo apt install nala -y || true

sudo nala install -y \
  curl wget gpg lsb-release apt-transport-https \
  samba fuse3 nfs-common \
  git net-tools htop nano \
  build-essential \
  python3-dev \
  unzip \
  pkg-config \
  libssl-dev || true
# nala depends on python and occasionally fails.

sudo apt install -y \
  curl wget gpg lsb-release apt-transport-https \
  samba fuse3 nfs-common \
  git net-tools htop nano \
  build-essential \
  python3-dev \
  unzip \
  pkg-config \
  libssl-dev || true

curl -fsSL https://bun.com/install | bash
. ~/.bashrc || true
sudo ln -s ~/.bun/bin/bun /usr/local/bin/node  # trick programs that expect node to use bun runtime.

# echo 'keyboard-configuration keyboard-configuration/layout select US English' | sudo debconf-set-selections
# echo 'keyboard-configuration keyboard-configuration/layoutcode string us' | sudo debconf-set-selections
# sudo DEBIAN_FRONTEND=noninteractive nala install cmatrix hollywood ffmpeg -y  make || true
