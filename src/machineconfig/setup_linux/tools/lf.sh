
source $(dirname $0)/get_latest_release.sh
r=$(get_latest_release "gokcehan/lf")

cd ~
mkdir tmpasdfisrdugne
cd tmpasdfisrdugne
wget https://github.com/gokcehan/lf/releases/download/$r/lf-linux-amd64.tar.gz -O lf-linux-amd64.tar.gz
tar xvf lf-linux-amd64.tar.gz
chmod +x lf
sudo mv lf /usr/local/bin
cd ~
rm -rdf tmpasdfisrdugne
