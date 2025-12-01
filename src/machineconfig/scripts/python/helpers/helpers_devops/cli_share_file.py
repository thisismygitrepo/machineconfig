
import typer
from typing import Annotated, Literal


def share_file_receive(code_args: Annotated[list[str], typer.Argument(help="Receive code or relay command. Examples: '7121-donor-olympic-bicycle' or '--relay 10.17.62.206:443 7121-donor-olympic-bicycle'")],
) -> None:
    """Receive a file using croc with relay server.
Usage examples:
    devops network receive 7121-donor-olympic-bicycle
    devops network receive -- --relay 10.17.62.206:443 7121-donor-olympic-bicycle
    devops network receive -- croc --relay 10.17.62.206:443 7121-donor-olympic-bicycle
"""
    from machineconfig.utils.installer_utils.installer_cli import install_if_missing
    install_if_missing(which="croc")
    import platform
    import sys

    is_windows = platform.system() == "Windows"

    # If no args passed via typer, try to get them from sys.argv directly
    # This handles the case where -- was used and arguments weren't parsed by typer
    if not code_args or (len(code_args) == 1 and code_args[0] in ['--relay', 'croc']):
        # Find the index of 'rx' or 'receive' in sys.argv and get everything after it
        try:
            for i, arg in enumerate(sys.argv):
                if arg in ['rx', 'receive', 'r'] and i + 1 < len(sys.argv):
                    code_args = sys.argv[i + 1:]
                    break
        except Exception:
            pass

    # Join all arguments
    input_str = " ".join(code_args)
    tokens = input_str.split()

    # Parse input to extract relay server and secret code
    relay_server: str | None = None
    secret_code: str | None = None

    # Remove 'croc' and 'export' from tokens if present
    tokens = [t for t in tokens if t not in ['croc', 'export']]

    # Look for --relay flag and capture next token
    relay_idx = -1
    for i, token in enumerate(tokens):
        if token == '--relay' and i + 1 < len(tokens):
            relay_server = tokens[i + 1]
            relay_idx = i
            break

    # Look for CROC_SECRET= prefix in any token
    for token in tokens:
        if token.startswith('CROC_SECRET='):
            secret_code = token.split('=', 1)[1].strip('"').strip("'")
            break

    # If no secret code found yet, look for tokens with dashes (typical pattern: number-word-word-word)
    # Skip relay server and relay flag
    if not secret_code:
        for i, token in enumerate(tokens):
            if '-' in token and not token.startswith('-') and token != relay_server:
                if relay_idx >= 0 and (i == relay_idx or i == relay_idx + 1):
                    continue  # Skip relay server parts
                secret_code = token
                break

    if not secret_code and not relay_server:
        typer.echo(f"❌ Error: Could not parse croc receive code from input: {input_str}", err=True)
        typer.echo("Usage:", err=True)
        typer.echo("  devops network receive 7121-donor-olympic-bicycle", err=True)
        typer.echo("  devops network receive -- --relay 10.17.62.206:443 7121-donor-olympic-bicycle", err=True)
        raise typer.Exit(code=1)

    # Build the appropriate script for current OS
    if is_windows:
        # Windows PowerShell format: croc --relay server:port secret-code --yes
        relay_arg = f"--relay {relay_server}" if relay_server else ""
        code_arg = f"{secret_code}" if secret_code else ""
        script = f"""croc {relay_arg} {code_arg} --yes""".strip()
    else:
        # Linux/macOS Bash format: CROC_SECRET="secret-code" croc --relay server:port --yes
        relay_arg = f"--relay {relay_server}" if relay_server else ""
        if secret_code:
            script = f"""export CROC_SECRET="{secret_code}"
croc {relay_arg} --yes""".strip()
        else:
            script = f"""croc {relay_arg} --yes""".strip()

    from machineconfig.utils.code import exit_then_run_shell_script, print_code
    print_code(code=script, desc="🚀 Receiving file with croc", lexer="bash" if platform.system() != "Windows" else "powershell")
    exit_then_run_shell_script(script=script, strict=False)


def share_file_send(path: Annotated[str, typer.Argument(help="Path to the file or directory to send")],
                    zip_folder: Annotated[bool, typer.Option("--zip", help="Zip folder before sending")] = False,
                    code: Annotated[str | None, typer.Option("--code", "-c", help="Codephrase used to connect to relay")] = None,
                    text: Annotated[str | None, typer.Option("--text", "-t", help="Send some text")] = None,
                    qrcode: Annotated[bool, typer.Option("--qrcode", "--qr", help="Show receive code as a qrcode")] = False,
                    backend: Annotated[Literal["wormhole", "w", "croc", "c"], typer.Option("--backend", "-b", help="Backend to use")] = "croc",
                    ) -> None:
    """Send a file using croc with relay server."""
    import platform

    match backend:
        case "wormhole" | "w":
            if code is None: code_line = ""
            else: code_line = f"--code {code}"
            if text is not None: text_line = f"--text '{text}'"
            else: text_line = f"'{path}'"
            script = f"""
uvx magic-wormhole send {code_line} {text_line}
"""
            print(f"🚀 Sending file: {path}. Use: uvx magic-wormhole receive ")
        case "croc" | "c":
            from machineconfig.utils.installer_utils.installer_cli import install_if_missing
            install_if_missing(which="croc")

            # Get relay server IP from environment or use default
            import machineconfig.scripts.python.helpers.helpers_network.address as helper
            res = helper.select_lan_ipv4(prefer_vpn=False)
            if res is None:
                typer.echo("❌ Error: Could not determine local LAN IPv4 address for relay.", err=True)
                raise typer.Exit(code=1)
            local_ip_v4 = res
            relay_port = "443"
            is_windows = platform.system() == "Windows"
            # Build command parts
            relay_arg = f"--relay {local_ip_v4}:{relay_port} --ip {local_ip_v4}:{relay_port}"
            zip_arg = "--zip" if zip_folder else ""
            text_arg = f"--text '{text}'" if text else ""
            qrcode_arg = "--qrcode" if qrcode else ""
            path_arg = f"{path}" if not text else ""

            if is_windows:
                # Windows PowerShell format
                code_arg = f"--code {code}" if code else ""
                script = f"""croc {relay_arg} send {zip_arg} {code_arg} {qrcode_arg} {text_arg} {path_arg}"""
            else:
                # Linux/macOS Bash format
                if code:
                    script = f"""
export CROC_SECRET="{code}"
croc {relay_arg} send {zip_arg} {qrcode_arg} {text_arg} {path_arg}"""
                else:
                    script = f"""croc {relay_arg} send {zip_arg} {qrcode_arg} {text_arg} {path_arg}"""

    typer.echo(f"🚀 Sending file: {path}. Use: devops network receive")
    from machineconfig.utils.code import exit_then_run_shell_script, print_code
    print_code(code=script, desc="🚀 sending file with croc", lexer="bash" if platform.system() != "Windows" else "powershell")
    exit_then_run_shell_script(script=script, strict=False)
