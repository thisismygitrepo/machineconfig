

get_latest_release() {
  curl --silent "https://api.github.com/repos/$1/releases/latest" | # Get latest release from GitHub api
    grep '"tag_name":' |                                            # Get tag line
    sed -E 's/.*"([^"]+)".*/\1/'                                    # Pluck JSON value
}

# ---------------------- diskonaut, a disk usage analyzer ------------------------
cd ~; mkdir tmp_asdf; cd tmp_asdf
latest=$(get_latest_release "imsnif/diskonaut")
wget https://github.com/imsnif/diskonaut/releases/download/$latest/diskonaut-$latest-unknown-linux-musl.tar.gz
tar -xvzf *
chmod +x ./diskonaut
sudo mv ./diskonaut /usr/local/bin/
cd ~; rm -rdf tmp_asdf
