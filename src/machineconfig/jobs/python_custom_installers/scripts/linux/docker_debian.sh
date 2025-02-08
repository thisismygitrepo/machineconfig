#!/bin/bash
# filepath: /home/alex/code/machineconfig/src/machineconfig/jobs/python_custom_installers/scripts/linux/docker_debian.sh

set -e

# Update package list and install prerequisites
sudo nala update
sudo nala install ca-certificates curl gnupg -y

# Create the keyrings directory (if not already present)
sudo install -m 0755 -d /etc/apt/keyrings

# Add Docker's official GPG key for Debian
sudo curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set the Debian version to "bookworm"
OS_NAME=bookworm

# Add Docker's repository for Debian to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $OS_NAME stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package list again to include the new repository:
sudo nala update

# Install Docker packages:
sudo nala install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y

# Enable and start Docker
sudo systemctl enable docker
sudo systemctl start docker

# Run a test container
docker run hello-world

# Create the docker user group and add the current user:
sudo groupadd docker || true
sudo usermod -aG docker $USER

echo "Docker installation on Debian Bookworm is complete."
