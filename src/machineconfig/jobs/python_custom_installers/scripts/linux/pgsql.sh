

# as per https://www.postgresql.org/download/linux/ubuntu/

# TO REMOVE:
# sudo apt-get --purge remove postgresql postgresql-*


# PG_VERSION=14  # ubbuntu 24 has 16 repo by default
# in 24, its simple 
# get_ubuntu_base_version() {
#     local mint_codename=$(lsb_release -cs)
#     case "$mint_codename" in
#         "wilma")
#             echo "noble"
#             ;;
#         "virginia")
#             echo "jammy"
#             ;;
#         *)
#             echo "$mint_codename"
#             ;;
#     esac
# }
# ubuntu_version=$(get_ubuntu_base_version)

sudo apt install -y postgresql-common
sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh

# sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $ubuntu_version-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
# curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg

# sudo nala update
# sudo nala install postgresql-16 postgresql-contrib-16


sudo nala install postgresql -y
