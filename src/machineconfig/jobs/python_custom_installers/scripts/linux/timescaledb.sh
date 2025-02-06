
# as per: https://docs.timescale.com/self-hosted/latest/install/installation-linux/#install-timescaledb-on-linux

get_ubuntu_base_version() {
    local os_codename=$(lsb_release -cs)
    case "$os_codename" in
        "wilma")
            echo "noble"  # Map Mint Wilma to the base image Ubuntu 24.04 LTS
            ;;
        "virginia")
            echo "jammy"  # Map Mint Jammy tothe base image Ubuntu 22.04 LTS
            ;;
        "bookworm")
            echo "jammy"  # Map Debian 12 to Ubuntu 22.04 LTS
            ;;
        *)
            echo "$os_codename"
            ;;
    esac
}

ubuntu_version=$(get_ubuntu_base_version)

echo "deb https://packagecloud.io/timescale/timescaledb/ubuntu/ $ubuntu_version main" | sudo tee /etc/apt/sources.list.d/timescaledb.list
wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/timescaledb.gpg

sudo nala update
sudo apt install timescaledb-2-postgresql-16 postgresql-client-16
sudo timescaledb-tune
sudo systemctl restart postgresql
sudo -u postgres psql
