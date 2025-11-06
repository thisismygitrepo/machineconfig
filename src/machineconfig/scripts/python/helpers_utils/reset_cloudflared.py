
code = """


cloudflared login  # creates new cert.pem @ $home_dir/.cloudflared/cert.pem
cloudflared tunnel create nw-tunnel  # creates a UUID.json credentials file @ $home_dir/.cloudflared/
hx ~/.cloudflared/config.yml

cloudflared tunnel route dns glenn  # creates CNAMES in Cloudflare dashboard

# test: cloudflared tunnel run glenn
home_dir=$HOME
cloudflared_path="$home_dir/.local/bin/cloudflared"
sudo $cloudflared_path service uninstall
sudo rm /etc/cloudflared/config.yml || true
sudo $cloudflared_path --config $home_dir/.cloudflared/config.yml service install

sudo cp $home_dir/.cloudflared/config.yml /etc/cloudflared/config.yml
# verify service is running
sudo systemctl status cloudflared --no-pager -l
sudo chown -R alex:alex /home/alex/.cloudflared/
sudo chmod 600 /home/alex/.cloudflared/*.json
sudo chmod 600 /home/alex/.cloudflared/cert.pem
sudo chmod 600 /home/alex/.cloudflared/config.yml



# upon making changes to config.yml,
# check syntax before restarting (recommended)
cloudflared tunnel --config /home/alex/.cloudflared/config.yml ingress validate
# then restart the service
sudo systemctl restart cloudflared
# confirm it's running again
sudo systemctl status cloudflared --no-pager -l


# WARP and tunnel don't work nicely, to solve:

option A: Completely disconnect WARP on that machine when running cloudflared.

Stop WARP: warp-cli disconnect (or via GUI)

Then start the tunnel and verify it works.

option b: Use split-tunnel or route exclusions in WARP so that cloudflared traffic is not routed through WARP.

In the WARP configuration (or via the Zero-Trust dashboard if managed) exclude the cloudflared process or the QUIC/UDP port range (default UDP 7844) from WARP.

See Cloudflare docs: in the “Unable to connect WARP” section, they note a third-party VPN interfering with WARP is a common cause. 
Cloudflare Docs
+1

On Reddit: user “traffic behaviour … shows no UDP 7844 traffic … seems like WARP is redirecting tunnel traffic through itself.” 
Reddit

option c: Force cloudflared to use HTTP/2 (TCP) fallback, which avoids UDP/QUIC and may work while WARP is connected:

In cloudflared config:

protocol: http2


Or via CLI: cloudflared tunnel run --protocol http2 …

This won’t use the UDP path so it may bypass the WARP conflict, albeit with potentially different performance.


"""