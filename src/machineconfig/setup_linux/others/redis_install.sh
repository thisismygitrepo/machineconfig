

# as per https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-linux/
# sudo apt-get install lsb-release curl gpg

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
sudo nala install redis

