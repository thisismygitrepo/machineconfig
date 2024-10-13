
# as per: https://docs.timescale.com/self-hosted/latest/install/installation-linux/#install-timescaledb-on-linux

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

echo "deb https://packagecloud.io/timescale/timescaledb/ubuntu/ $ubuntu_version main" | sudo tee /etc/apt/sources.list.d/timescaledb.list
wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/timescaledb.gpg

sudo nala update
sudo apt install timescaledb-2-postgresql-16 postgresql-client-16
sudo timescaledb-tune
sudo systemctl restart postgresql
sudo -u postgres psql
