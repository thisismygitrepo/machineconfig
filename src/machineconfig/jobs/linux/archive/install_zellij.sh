
get_latest_release() {
  curl --silent "https://api.github.com/repos/$1/releases/latest" | # Get latest release from GitHub api
    grep '"tag_name":' |                                            # Get tag line
    sed -E 's/.*"([^"]+)".*/\1/'                                    # Pluck JSON value
}

# ------------ zellij, a terminal multiplexer ------------
cd ~; mkdir "tmp_asdf"; cd tmp_asdf
wget https://github.com/zellij-org/zellij/releases/latest/download/zellij-x86_64-unknown-linux-musl.tar.gz
tar -xvzf *; chmod +x ./zellij; sudo mv ./zellij /usr/local/bin/; cd ~; rm -rdf tmp_asdf

