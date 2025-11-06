
code = """


cloudflared login  # creates new cert.pem @ $home_dir/.cloudflared/cert.pem
cloudflared tunnel create nw-tunnel  # creates a UUID.json credentials file @ $home_dir/.cloudflared/
hx ~/.cloudflared/config.yml

cloudflared tunnel route dns glenn

# test: cloudflared tunnel run glenn
home_dir=$HOME
cloudflared_path="$home_dir/.local/bin/cloudflared"
sudo $cloudflared_path service uninstall
sudo rm /etc/cloudflared/config.yml || true
sudo $cloudflared_path --config $home_dir/.cloudflared/config.yml service install


# upon making changes to config.yml,
# check syntax before restarting (recommended)
cloudflared tunnel --config /home/alex/.cloudflared/config.yml ingress validate
# then restart the service
sudo systemctl restart cloudflared
# confirm it's running again
sudo systemctl status cloudflared --no-pager -l

"""