

import platform
from typing import Optional
import tomllib
from pathlib import Path
from machineconfig.utils.accessories import randstr
from machineconfig.utils.options import choose_from_options


def choose_function_or_lines(choice_file: Path, kwargs_dict: dict[str, object]) -> tuple[Optional[str], Path, dict[str, object]]:
    """
    Choose a function to run from a Python file or lines from a shell script.
    
    Returns:
        tuple: (choice_function, choice_file, kwargs_dict)
        - choice_function: The selected function name or None
        - choice_file: The file path (potentially modified for shell scripts)
        - kwargs_dict: Updated kwargs dictionary with user-provided arguments
    """
    choice_function: Optional[str] = None
    
    if choice_file.suffix == ".py":
        from machineconfig.scripts.python.helpers.helpers_fire_command.file_wrangler import parse_pyfile
        options, func_args = parse_pyfile(file_path=str(choice_file))
        choice_function_tmp = choose_from_options(msg="Choose a function to run", options=options, tv=True, multi=False)
        assert isinstance(choice_function_tmp, str), f"choice_function must be a string. Got {type(choice_function_tmp)}"
        choice_index = options.index(choice_function_tmp)
        choice_function = choice_function_tmp.split(" -- ")[0]
        choice_function_args = func_args[choice_index]

        if choice_function == "RUN AS MAIN":
            choice_function = None
        if len(choice_function_args) > 0 and len(kwargs_dict) == 0:
            for item in choice_function_args:
                kwargs_dict[item.name] = input(f"Please enter a value for argument `{item.name}` (type = {item.type}) (default = {item.default}) : ") or item.default
    elif choice_file.suffix == ".sh":
        options = []
        for line in choice_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("#"):
                continue
            if line == "":
                continue
            if line.startswith("echo"):
                continue
            options.append(line)
        chosen_lines = choose_from_options(msg="Choose a line to run", options=options, tv=True, multi=True)
        choice_file = Path.home().joinpath(f"tmp_results/tmp_scripts/shell/{randstr(10)}.sh")
        choice_file.parent.mkdir(parents=True, exist_ok=True)
        choice_file.write_text("\n".join(chosen_lines), encoding="utf-8")
        choice_function = None
    
    return choice_function, choice_file, kwargs_dict


def get_command_streamlit(choice_file: Path, environment: str, repo_root: Optional[Path]) -> str:
    # from machineconfig.scripts.python.helpers.helpers_utils.path import get_machine_specs
    from machineconfig.scripts.python.helpers.helpers_network.address import select_lan_ipv4
    res = select_lan_ipv4(prefer_vpn=False)
    if res is None:
        raise RuntimeError("Could not determine local LAN IPv4 address for streamlit app.")
    local_ip_v4 = res

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
            secrets_template_path = Path.home().joinpath(f"dotfiles/creds/streamlit/{Path(repo_root).name}/{choice_file.name}/secrets.toml")
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
    from machineconfig.utils.installer_utils.installer_cli import install_if_missing
    install_if_missing("qrterminal")
    script = f"""
qrterminal "http://{local_ip_v4}:{port}"
echo "http://{local_ip_v4}:{port}"
qrterminal "http://{computer_name}:{port}"
echo "http://{computer_name}:{port}"
"""
    # from machineconfig.utils.code import run_shell_script
    # run_shell_script(script)
    from machineconfig.utils.code import print_code
    print_code(code=script, lexer="shell", desc="Streamlit QR Codes and URLs")

    message = f"🚀 Streamlit app is running @:\n1- http://{local_ip_v4}:{port}\n2- http://{computer_name}:{port}\n3- http://localhost:{port}"
    from rich.panel import Panel
    from rich import print as rprint

    rprint(Panel(message))
    exe = f"streamlit run --server.address 0.0.0.0 --server.headless true --server.port {port}"
    # exe = f"cd '{choice_file.parent}'; " + exe
    return exe
