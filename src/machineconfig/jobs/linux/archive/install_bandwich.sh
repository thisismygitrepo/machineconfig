

get_latest_release() {
  curl --silent "https://api.github.com/repos/$1/releases/latest" | # Get latest release from GitHub api
    grep '"tag_name":' |                                            # Get tag line
    sed -E 's/.*"([^"]+)".*/\1/'                                    # Pluck JSON value
}


# -------------------- banchwich, a network usage monitor
cd ~; mkdir tmp_asdf; cd tmp_asdf
latest=$(get_latest_release "imsnif/bandwhich")
wget https://github.com/imsnif/bandwhich/releases/download/$latest/bandwhich-v$latest-x86_64-unknown-linux-musl.tar.gz
tar -xvzf *
chmod +x ./bandwhich
sudo mv ./bandwhich /usr/local/bin/
cd ~; rm -rdf tmp_asdf