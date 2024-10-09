

# as per https://www.postgresql.org/download/linux/ubuntu/

# TO REMOVE:
# sudo apt-get --purge remove postgresql postgresql-*


sudo nala install postgresql-common -y
sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh -y
sudo nala install postgresql-17 -y

# sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $ubuntu_version-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
# curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg
# sudo nala update
# sudo nala install postgresql-contrib-16 -y


# The following gives results that are OS dependent (e.g. Ubuntu 20.04, 22.04, etc, gives v15, v16, v17 etc):
# sudo nala install postgresql-common -y
# sudo nala install postgresql -y
