#!/usr/bin/bash

# as per https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-linux/
# works for Both debian and Ubuntu

get_ubuntu_base_version() {
    local mint_codename=$(lsb_release -cs)
    case "$mint_codename" in
        "wilma")
            echo "noble"
            ;;
        "virginia")
            echo "jammy"
            ;;
        *)
            echo "$mint_codename"
            ;;
    esac
}
ubuntu_version=$(get_ubuntu_base_version)


curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
sudo chmod 644 /usr/share/keyrings/redis-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $ubuntu_version main" | sudo tee /etc/apt/sources.list.d/redis.list
sudo nala update
sudo nala install redis -y

echo "ℹ️ To start redis server:           sudo systemctl start redis-server"
echo "ℹ️ To stop redis server:            sudo systemctl stop redis-server"
echo "ℹ️ To restart redis server:         sudo systemctl restart redis-server"
echo "ℹ️ To check status of redis server: sudo systemctl status redis-server"
echo "ℹ️ To start on boot:                sudo systemctl enable --now redis-server"
