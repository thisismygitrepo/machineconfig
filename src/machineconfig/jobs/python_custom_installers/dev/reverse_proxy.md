

given terminal access to a remote computer in my home in australia, and using frpc and frps, give me commands (no config files) to start a proxy server that enable me to access a website https://example.com.au that is only available in Australia, so I can access it from my vocation house in iraq. I have http port 8100 on my computer in australia accesssible securely to me everywhere through cloudflare.


# Start frps to listen on port 8100
./frps -p 8100
./frps --bind_addr 0.0.0.0 --bind_port 8100 --token "yoursecretqwe"

# Start frpc with HTTP proxy configuration
./frpc http --server_addr "AUSTRALIA_MACHINE_DOMAIN_OR_IP:8100" \
     --token "yoursecret" \
     --local_port 8080 \
     --plugin http_proxy \
     --plugin_local_addr "example.com.au:443" \
     --plugin_host_header "example.com.au"

# Start local proxy to forward traffic
ssh -L 8080:example.com.au:443 localhost
# Now you can access the Australian site through: https://localhost:8080


---


./frps --bind_port=7000 --token=secret

./frpc http selfservice.hrms.sa.gov.au/PROD2:443 \
  --server_addr=127.0.0.1 --server_port=7000 \
  --token=secret

