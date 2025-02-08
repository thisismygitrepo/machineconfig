# https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository

# # Add Docker's official GPG key:
# sudo nala update
# sudo nala install ca-certificates curl gnupg -y
# sudo install -m 0755 -d /etc/apt/keyrings
# curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
# sudo chmod a+r /etc/apt/keyrings/docker.gpg

# # $OS_NAME=$(lsb_release -cs)
# # $OS_NAME=$(. /etc/os-release && echo "$VERSION_CODENAME")
# $OS_NAME=jammy  # verigina doens't work

# # Add the repository to Apt sources:
# echo \
#   "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
#    $OS_NAME stable" | \
#   sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
# sudo nala update

# sudo nala install docker-ce docker-ce-cli containerd.io docker- buildx-plugin docker-compose-plugin -y

get_os_type() {
    if [ -f /etc/debian_version ]; then
        echo "debian"
    elif [ -f /etc/lsb-release ]; then
        echo "ubuntu"
    else
        echo "unsupported"
    fi
}

get_ubuntu_base_version() {
    local os_codename=$(lsb_release -cs)
    case "$os_codename" in
        "wilma")
            echo "noble"  # Map Mint Wilma to the base image Ubuntu 24.04 LTS
            ;;
        "virginia")
            echo "jammy"  # Map Mint virginia to the base image Ubuntu 22.04 LTS
            ;;
        *)
            echo "$os_codename"
            ;;
    esac
}

os_type=$(get_os_type)
if [ "$os_type" = "unsupported" ]; then
    echo "Unsupported OS type"
    exit 1
fi

if [ "$os_type" = "ubuntu" ]; then
    ubuntu_version=$(get_ubuntu_base_version)
    repo_url="https://download.docker.com/linux/ubuntu"
else
    ubuntu_version=$(lsb_release -cs)
    repo_url="https://download.docker.com/linux/debian"
fi

echo "OS type: $os_type"
echo "Version: $ubuntu_version"

# Add Docker's official GPG key:
sudo nala update
sudo nala install ca-certificates curl -y

# sudo mkdir -p /etc/apt/keyrings  # USE IF THINGS GET MESSY,  THIS DOES OVERWRITING
sudo install -m 0755 -d /etc/apt/keyrings
# sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo curl -fsSL $repo_url/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] $repo_url \
  $ubuntu_version stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo nala update
sudo nala install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y

sudo systemctl enable docker
docker run hello-world
sudo groupadd docker
sudo usermod -aG docker $USER

# As per NixOs installer:
# nix-env -iA nixpkgs.docker
# # as per: https://docs.docker.com/engine/install/linux-postinstall/
# sudo groupadd docker
# sudo usermod -aG docker $USER
# # Now you need to log out and in OR run: `newgrp docker`
# 


# in older wsl, following installation, docker run hello-world will fail with error:
# https://stackoverflow.com/questions/44678725/cannot-connect-to-the-docker-daemon-at-unix-var-run-docker-sock-is-the-docker
# You need to run the following command to fix it: systemctl start dockerd
# However, in newer wsl, systemctl is not available. One can start it but it adds to much cluttering services not needed in wsl.
# one way to get around it https://askubuntu.com/questions/1379425/system-has-not-been-booted-with-systemd-as-init-system-pid-1-cant-operate
# is adding the script docker.sh to /etc/init.d/dockerd

# no internet in wsl docker instance: add /etc/docker/daemon.json
# https://github.com/MicrosoftDocs/WSL/issues/422

# lastly, to avoid cases where sudo is needed for every docker command
# sudo usermod -a -G docker $USER  # then reboot
# this is as per: https://stackoverflow.com/questions/47854463/docker-got-permission-denied-while-trying-to-connect-to-the-docker-daemon-socke

# databricks only:
# sudo nala install fuse-overlayfs

