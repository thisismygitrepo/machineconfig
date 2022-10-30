
get_latest_release() {
  curl --silent "https://api.github.com/repos/$1/releases/latest" | # Get latest release from GitHub api
    grep '"tag_name":' |                                            # Get tag line
    sed -E 's/.*"([^"]+)".*/\1/'                                    # Pluck JSON value
}


# ------------------- nushell, structured data shell -------------------
cd ~; mkdir "tmp_asdf"; cd tmp_asdf
latest=$(get_latest_release "nushell/nushell")
wget https://github.com/nushell/nushell/releases/download/$latest/nu-$latest-x86_64-unknown-linux-gnu.tar.gz
tar -xvzf *; chmod +x ./nu; sudo mv ./nu /usr/local/bin/; cd ~; rm -rdf tmp_asdf
