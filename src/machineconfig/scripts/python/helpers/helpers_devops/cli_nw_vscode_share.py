import platform
import shlex
from pathlib import Path
from urllib.parse import quote


def ensure_without_connection_token(extra_args: str) -> str:
    tokens = shlex.split(extra_args) if extra_args.strip() else []
    if any(
        token == "--without-connection-token"
        or token == "--connection-token"
        or token.startswith("--connection-token=")
        or token == "--connection-token-file"
        or token.startswith("--connection-token-file=")
        for token in tokens
    ):
        return extra_args
    if extra_args.strip():
        return f"--without-connection-token {extra_args}".strip()
    return "--without-connection-token"


def _extract_option_value(args: list[str], option: str) -> str | None:
    for index, token in enumerate(args):
        if token == option and index + 1 < len(args):
            return args[index + 1]
        if token.startswith(f"{option}="):
            return token.split("=", 1)[1]
    return None


def _get_serve_web_details(cmd: str) -> tuple[str, int, str]:
    tokens = shlex.split(cmd)
    host = _extract_option_value(tokens, "--host") or "localhost"
    port_raw = _extract_option_value(tokens, "--port")
    server_base_path = _extract_option_value(tokens, "--server-base-path") or ""

    try:
        port = int(port_raw) if port_raw is not None else 8000
    except ValueError:
        port = 8000

    return host, port, server_base_path


def _normalize_server_base_path(server_base_path: str) -> str:
    trimmed = server_base_path.strip()
    if trimmed in {"", "/"}:
        return ""
    return "/" + trimmed.strip("/")


def resolve_share_local_folder(directory: str | None) -> str:
    if directory is None or directory.strip() == "":
        return str(Path.cwd().resolve())
    return str(Path(directory).expanduser().resolve(strict=False))


def _build_http_url(host: str, port: int, server_base_path: str, folder_path: str | None) -> str:
    normalized_path = _normalize_server_base_path(server_base_path)
    suffix = "/" if normalized_path == "" else f"{normalized_path}/"
    url = f"http://{host}:{port}{suffix}"
    if folder_path is not None:
        encoded_folder = quote(folder_path, safe="/:")
        url = f"{url}?folder={encoded_folder}"
    return url


def print_serve_web_urls(cmd: str, folder_path: str | None) -> None:
    from rich import box
    from rich.console import Console, Group
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    import machineconfig.scripts.python.helpers.helpers_network.address as helper

    host, port, server_base_path = _get_serve_web_details(cmd)
    normalized_host = host.strip().lower()
    base_path_note = _normalize_server_base_path(server_base_path) or "/"
    console = Console()
    address_warning: Text | None = None

    if port == 0:
        console.print(
            Panel(
                Group(
                    Text("`code serve-web` is configured to pick a random free port.", style="bold yellow"),
                    Text("The final clickable URL will only be known after the server starts.", style="yellow"),
                    Text(f"Base path: {base_path_note}", style="dim"),
                    Text(f"Folder: {folder_path}", style="dim") if folder_path is not None else Text("", style="dim"),
                ),
                title="VS Code Web URLs",
                border_style="yellow",
            )
        )
        return

    urls: list[tuple[str, str]] = []
    seen_urls: set[str] = set()

    def add_url(label: str, target_host: str) -> None:
        url = _build_http_url(target_host, port, server_base_path, folder_path)
        if url in seen_urls:
            return
        seen_urls.add(url)
        urls.append((label, url))

    try:
        all_ipv4 = helper.get_all_ipv4_addresses()
    except Exception as exc:
        all_ipv4 = []
        address_warning = Text(f"Could not enumerate interface IPv4 addresses: {exc}", style="yellow")

    if normalized_host in {"", "localhost", "127.0.0.1"}:
        add_url("Localhost", "localhost")
        for iface, ip in all_ipv4:
            if ip.startswith("127."):
                add_url(iface, ip)
    elif normalized_host == "0.0.0.0":
        add_url("Localhost", "localhost")
        computer_name = platform.node().strip()
        if computer_name:
            add_url("Hostname", computer_name)
        for iface, ip in all_ipv4:
            if ip.startswith("127."):
                continue
            add_url(iface, ip)
    else:
        add_url("Configured host", host)

    table = Table(box=box.SIMPLE_HEAVY, expand=True)
    table.add_column("Target", style="cyan", no_wrap=True)
    table.add_column("URL", style="bright_blue")

    for label, url in urls:
        link_text = Text(url, style="bold bright_blue")
        link_text.stylize(f"link {url}")
        table.add_row(label, link_text)

    binding_note = (
        f"Bound to {host}. Open these after the server starts."
        if normalized_host != "0.0.0.0"
        else "Bound to 0.0.0.0, so localhost and each non-loopback IPv4 can be used from this machine or your LAN."
    )
    note = Text(f"Base path: {base_path_note}    Port: {port}", style="dim")
    body = [Text(binding_note, style="bold green"), table]
    if address_warning is not None:
        body.append(address_warning)
    if folder_path is not None:
        body.append(Text(f"Folder: {folder_path}", style="dim"))
    body.append(note)

    console.print(
        Panel(
            Group(*body),
            title="VS Code Web URLs",
            border_style="green",
        )
    )
