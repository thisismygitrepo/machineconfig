
from typing import Optional, TypedDict, cast

class CountryFlag(TypedDict, total=False):
    emoji: str
    unicode: str

class CountryCurrency(TypedDict, total=False):
    code: str
    symbol: str

class Continent(TypedDict, total=False):
    code: str
    name: str

class PublicIpInfo(TypedDict, total=True):
    ip: str
    hostname: str
    city: str
    region: str
    country: str
    country_name: str
    country_flag: CountryFlag
    country_flag_url: str
    country_currency: CountryCurrency
    continent: Continent
    loc: str
    org: str
    postal: str
    timezone: str


def get_public_ip_address() -> PublicIpInfo:
    from machineconfig.utils.installer_utils.installer_cli import install_if_missing
    import subprocess
    install_if_missing("ipinfo")
    result = subprocess.run(
        ["ipinfo", "myip", "--json"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    import json
    loaded_json: PublicIpInfo = json.loads(result.stdout)
    return loaded_json


def get_all_ipv4_addresses() -> list[tuple[str, str]]:
    import psutil
    import socket
    result: list[tuple[str, str]] = []
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                ip = addr.address
                result.append((iface, ip))
    return result


def select_lan_ipv4(prefer_vpn: bool) -> Optional[str]:
    """
    Choose the best 'real LAN' IPv4:
      - Excludes loopback/link-local and (by default) VPN/tunnel/container ifaces
      - Prefers physical-looking ifaces (eth/en*/wlan/wl*)
      - Prefers RFC1918 LANs: 192.168/16 > 10/8 > 172.16/12
      - Requires interface is UP
    Set prefer_vpn=True to allow tunnel/VPN ifaces to compete.
    """

    import ipaddress
    import re
    from collections.abc import Sequence
    import psutil

    # Down-rank or exclude: tunnels/VPNs/bridges/containers (add your own if needed)
    VIRTUAL_IFACE_PAT = re.compile(
        r"^(?:lo|loopback|docker\d*|br-.*|veth.*|virbr.*|bridge.*|"
        r"vboxnet.*|vmnet.*|zt.*|ham.*|tailscale.*|wg\d*|utun\d*|llw\d*|awdl\d*|"
        r"tun\d*|tap\d*|cloudflarewarp.*|warp.*)$",
        re.IGNORECASE,
    )

    # Light preference for names that look like real NICs
    PHYSICAL_IFACE_PAT = re.compile(
        r"^(?:eth\d*|en\d*|enp.*|ens.*|eno.*|wlan\d*|wl.*|.*wifi.*|.*ethernet.*)$",
        re.IGNORECASE,
    )

    # Known noisy CIDRs to avoid
    NOISY_NETS: list[ipaddress.IPv4Network] = [
        ipaddress.IPv4Network("100.64.0.0/10"),   # CGNAT (Tailscale/others)
        ipaddress.IPv4Network("172.17.0.0/16"),   # docker0 default
        ipaddress.IPv4Network("172.18.0.0/16"),
        ipaddress.IPv4Network("172.19.0.0/16"),
        ipaddress.IPv4Network("192.168.49.0/24"), # minikube default
        ipaddress.IPv4Network("10.0.2.0/24"),     # VirtualBox NAT
    ]

    def _in_any(ip: ipaddress.IPv4Address, nets: Sequence[ipaddress.IPv4Network]) -> bool:
        return any(ip in n for n in nets)

    stats = psutil.net_if_stats()
    best = None
    best_score = -10**9
    import socket
    for iface, addrs in psutil.net_if_addrs().items():
        st = stats.get(iface)
        if not st or not st.isup:
            continue

        for a in addrs:
            if a.family != socket.AF_INET or not a.address:
                continue

            ip_str = a.address
            try:
                ip = cast(ipaddress.IPv4Address, ipaddress.ip_address(ip_str))
            except ValueError:
                continue

            # Exclude unusable classes
            if ip.is_loopback or ip.is_link_local:  # 127.0.0.0/8, 169.254.0.0/16
                continue

            # Hard filter: if it looks virtual and we don't prefer VPNs, skip it
            if not prefer_vpn and VIRTUAL_IFACE_PAT.match(iface):
                continue

            # Hard filter: known noisy subnets (docker, cgnat, etc.)
            if _in_any(ip, NOISY_NETS) and not prefer_vpn:
                continue

            # Base score
            score = 0

            # Prefer physical-looking names
            if PHYSICAL_IFACE_PAT.match(iface):
                score += 200

            # Broadcast present usually means L2 LAN (not point-to-point)
            # (psutil puts it on the same entry as .broadcast)
            if getattr(a, "broadcast", None):
                score += 100

            # Prefer private RFC1918; rank families
            if ip.is_private:
                # Order: 192.168.x.x > 10.x.x.x > 172.16-31.x.x
                ip_net = ipaddress.IPv4Network((ip, 32), strict=False)
                if ipaddress.IPv4Network("192.168.0.0/16").supernet_of(ip_net):
                    score += 90
                elif ipaddress.IPv4Network("10.0.0.0/8").supernet_of(ip_net):
                    score += 70
                elif ipaddress.IPv4Network("172.16.0.0/12").supernet_of(ip_net):
                    score += 50
            else:
                # Public on a NIC is unusual for a home/office LAN
                score -= 50

            # Slight nudge by interface speed if known (>0 means psutil knows it)
            # (Many tunnels report 0)
            if getattr(st, "speed", 0) > 0:
                score += 20

            # Deterministic tie-breaker: prefer shorter iface name (eth0 over eth10)
            score -= len(iface) * 0.01

            if score > best_score:
                best_score = score
                best = ip_str

    return best


if __name__ == "__main__":
    print(select_lan_ipv4(False) or "No LAN IPv4 found")
