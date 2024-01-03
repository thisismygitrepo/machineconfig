
#!/bin/sh

### BEGIN INIT INFO
# Provides:          docker
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start daemon at boot time
# Description:       Enable service provided by daemon.
### END INIT INFO

case "$1" in
  start)
    echo "Starting Docker..."
    /usr/bin/dockerd &
    ;;
  stop)
    echo "Stopping Docker..."
    killall dockerd
    ;;
  *)
    echo "Usage: /etc/init.d/docker {start|stop}"
    exit 1
    ;;
esac

exit 0




# https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository

# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg -y
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y

sudo docker run hello-world

# in older wsl, following installation, docker run hello-world will fail with error:
# https://stackoverflow.com/questions/44678725/cannot-connect-to-the-docker-daemon-at-unix-var-run-docker-sock-is-the-docker
# You need to run the following command to fix it: systemctl start dockerd
# However, in newer wsl, systemctl is not available. One can start it but it adds to much cluttering services not needed in wsl.
# one wat to get around it https://askubuntu.com/questions/1379425/system-has-not-been-booted-with-systemd-as-init-system-pid-1-cant-operate
# is adding the script docker.sh to /etc/init.d/dockerd

# lastly, to avoid cases where sudo is needed for every docker command
# sudo usermod -a -G docker $USER  # then reboot
# this is as per: https://stackoverflow.com/questions/47854463/docker-got-permission-denied-while-trying-to-connect-to-the-docker-daemon-socke

