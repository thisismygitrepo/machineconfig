
# ---------------------- kondo, a smart and automatic disk cleaner ------------------------
cd ~ || exit
mkdir "tmp_asdf"
cd tmp_asdf || exit
wget https://github.com/tbillington/kondo/releases/latest/download/kondo-x86_64-unknown-linux-gnu.tar.gz
tar -xvzf *
chmod +x ./kondo
sudo mv ./kondo /usr/local/bin/
cd ~ || exit
rm -rdf tmp_asdf

