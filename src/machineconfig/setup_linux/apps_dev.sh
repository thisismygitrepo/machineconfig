

# yes '' | sed 3q; echo "----------------------------- installing sharewifi ----------------------------"; yes '' | sed 3q
# npm install sharewifi -g || true

yes '' | sed 3q; echo "----------------------------- installing Thunderbird & Brave ----------------------------"; yes '' | sed 3q
#flatpak install flathub org.mozilla.Thunderbird
#flatpak install flathub com.brave.Browser
# ln -s /home/$USER/.nix-profile/share/applications/* /home/$USER/.local/share/applications/

yes '' | sed 3q; echo "----------------------------- installing github-copilot-cli ----------------------------"; yes '' | sed 3q
nix-env -iA nixpkgs.gh
# as per https://docs.github.com/en/copilot/github-copilot-in-the-cli/using-github-copilot-in-the-cli
# gh auth login
# gh extension install github/gh-copilot

yes '' | sed 3q; echo "----------------------------- installing easy-sharing ----------------------------"; yes '' | sed 3q
npm install -g easy-sharing  # https://github.com/parvardegr/sharing
# https://github.com/mifi/ezshare


yes '' | sed 3q; echo "----------------------------- installing sshfs ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  sudo apt install sshfs  # mount remote filesystems over ssh
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.sshfs || true
fi

yes '' | sed 3q; echo "----------------------------- installing samba ----------------------------"; yes '' | sed 3q
#sudo apt install samba  # LAN-based file sharing


yes '' | sed 3q; echo "----------------------------- installing cloudflared Warp --------------------------------"; yes '' | sed 3q
# as per Ubuntu of https://pkg.cloudflareclient.com/
curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | sudo gpg --yes --dearmor --output /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ jammy main" | sudo tee /etc/apt/sources.list.d/cloudflare-client.list
sudo apt-get update && sudo apt-get install cloudflare-warp -y

yes '' | sed 3q; echo "----------------------------- installing cloudflared -------------------------------"; yes '' | sed 3q
# install as per instructions. Advantage of avoiding a package manager is getting: cloudflared update command.
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb && sudo dpkg -i cloudflared-linux-amd64.deb


yes '' | sed 3q; echo "----------------------------- installing remmina--------------------------------"; yes '' | sed 3q
sudo apt install remmina remmina-plugin-rdp -y


yes '' | sed 3q; echo "----------------------------- installing graphviz ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  sudo apt install graphviz -y || true
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.graphviz || true
fi

yes '' | sed 3q; echo "----------------------------- installing make ----------------------------"; yes '' | sed 3q
sudo apt install make -y || true  # lvim and spacevim require it.

yes '' | sed 3q; echo "----------------------------- installing lynx ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  sudo apt install lynx -y || true  # tex browser, just like w3m
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.lynx || true
  ~/.nix-profile/bin/nix-env -iA nixpkgs.brave
fi

yes '' | sed 3q; echo "----------------------------- installing redis ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  # installation for ubuntu as per https://redis.io/docs/getting-started/installation/install-redis-on-linux/
  curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
  echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list
  sudo apt-get update
  sudo apt-get install redis -y
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.redis || true
fi



yes '' | sed 3q; echo "----------------------------- installing ncdu ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  sudo apt install ncdu -y || true   # disk usage analyzer, like diskonaut
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.ncdu || true
fi

# https://github.com/bootandy/dust
# https://github.com/dalance/procs#installation

yes '' | sed 3q; echo "----------------------------- installing exa ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  sudo apt install exa -y || true  # replacement for ls. no ner fonts, unlike lsd
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.exa || true
fi

yes '' | sed 3q; echo "----------------------------- installing navi ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
#  sudo apt install exa -y || true  # replacement for ls. no ner fonts, unlike lsd
  echo "no apt installer for navi, skipping"
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.navi || true
fi

yes '' | sed 3q; echo "----------------------------- installing just ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  sudo apt install just -y || true  # replacement for make
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.just || true
fi


yes '' | sed 3q; echo "----------------------------- installing hyperfine ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  sudo apt install curl
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.hyperfine  || true  # benchamrking
fi

# sudo apt install neovim -y  # nvim, but not latest release
# download neovim from release page
# sudo apt remove neovim
# sudo rm ~/.local/bin/nvim || true
yes '' | sed 3q; echo "----------------------------- installing nvim ----------------------------"; yes '' | sed 3q
# cd ~ || true
# wget https://github.com/neovim/neovim/releases/download/stable/nvim-linux64.deb || true
# sudo apt install ./nvim-linux64.deb || true
# rm nvim-linux64.deb || true
~/.nix-profile/bin/nix-env -iA nixpkgs.neovim



yes '' | sed 3q; echo "----------------------------- installing lunarvim ----------------------------"; yes '' | sed 3q
# from https://www.lunarvim.org/docs/installation
LV_BRANCH='release-1.2/neovim-0.8' bash <(curl -s https://raw.githubusercontent.com/lunarvim/lunarvim/master/utils/installer/install.sh)

yes '' | sed 3q; echo "----------------------------- installing spacevim ----------------------------"; yes '' | sed 3q
# https://spacevim.org/quick-start-guide/#linux-and-macos
(curl -sLf https://spacevim.org/install.sh | bash) || true


# ---------------------------- Programming Languages ------------------------------------
yes '' | sed 3q; echo "----------------------------- installing codon ----------------------------"; yes '' | sed 3q
/bin/bash -c "$(curl -fsSL https://exaloop.io/install.sh)"

yes '' | sed 3q; echo "----------------------------- installing rust ----------------------------"; yes '' | sed 3q
# curl https://sh.rustup.rs -sSf | sh
(curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh) || true

yes '' | sed 3q; echo "----------------------------- installing hollywood ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  sudo apt install hollywood -y || true  # for fun
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.hollywood || true
fi

