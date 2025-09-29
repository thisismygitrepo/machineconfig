

import platform
from typing import Optional
import tomllib
from pathlib import Path
from machineconfig.utils.accessories import randstr
from machineconfig.utils.path_extended import PathExtended


def get_command_streamlit(choice_file: Path, environment: str, repo_root: Optional[Path]) -> str:
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 1))
        local_ip_v4 = s.getsockname()[0]
    except Exception:
        local_ip_v4 = socket.gethostbyname(socket.gethostname())
    finally:
        s.close()
    computer_name = platform.node()
    port = 8501
    toml_path: Optional[Path] = None
    toml_path_maybe = choice_file.parent.joinpath(".streamlit/config.toml")
    if toml_path_maybe.exists():
        toml_path = toml_path_maybe
    elif choice_file.parent.name == "pages":
        toml_path_maybe = choice_file.parent.parent.joinpath(".streamlit/config.toml")
        if toml_path_maybe.exists():
            toml_path = toml_path_maybe
    if toml_path is not None:
        print(f"📄 Reading config.toml @ {toml_path}")
        config = tomllib.loads(toml_path.read_text(encoding="utf-8"))
        if "server" in config:
            if "port" in config["server"]:
                port = config["server"]["port"]
        secrets_path = toml_path.with_name("secrets.toml")
        if repo_root is not None:
            secrets_template_path = Path.home().joinpath(f"dotfiles/creds/streamlit/{PathExtended(repo_root).name}/{choice_file.name}/secrets.toml")
            if environment != "" and not secrets_path.exists() and secrets_template_path.exists():
                secrets_template = tomllib.loads(secrets_template_path.read_text(encoding="utf-8"))
                if environment == "ip":
                    host_url = f"http://{local_ip_v4}:{port}/oauth2callback"
                elif environment == "localhost":
                    host_url = f"http://localhost:{port}/oauth2callback"
                elif environment == "hostname":
                    host_url = f"http://{computer_name}:{port}/oauth2callback"
                else:
                    host_url = f"http://{environment}:{port}/oauth2callback"
                try:
                    secrets_template["auth"]["redirect_uri"] = host_url
                    secrets_template["auth"]["cookie_secret"] = randstr(35)
                    secrets_template["auth"]["auth0"]["redirect_uri"] = host_url
                    # save_toml(obj=secrets_template, path=secrets_path)
                except Exception as ex:
                    print(ex)
                    raise ex
    message = f"🚀 Streamlit app is running @:\n1- http://{local_ip_v4}:{port}\n2- http://{computer_name}:{port}\n3- http://localhost:{port}"
    from rich.panel import Panel
    from rich import print as rprint

    rprint(Panel(message))
    exe = f"streamlit run --server.address 0.0.0.0 --server.headless true --server.port {port}"
    # exe = f"cd '{choice_file.parent}'; " + exe
    return exe
