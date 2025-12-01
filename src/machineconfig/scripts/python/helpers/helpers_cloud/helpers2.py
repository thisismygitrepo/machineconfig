from machineconfig.scripts.python.helpers.helpers_cloud.cloud_helpers import Args, ArgsDefaults, absolute, find_cloud_config, get_secure_share_cloud_config
from machineconfig.utils.io import read_ini
from machineconfig.utils.source_of_truth import DEFAULTS_PATH
from machineconfig.utils.accessories import pprint
from typing import Optional
from rich.console import Console
from rich.panel import Panel


ES = "^"  # chosen carefully to not mean anything on any shell. `$` was a bad choice.
console = Console()


def parse_cloud_source_target(args: Args, source: str, target: str) -> tuple[str, str, str]:
    print("Source:", source)
    print("Target:", target)
    config = args.config
    if config == "ss":
        cloud_maybe: Optional[str] = target.split(":")[0]
        # if cloud_maybe == "": cloud_maybe = source.split(":")[0]
        if cloud_maybe == "":
            cloud_maybe = None
        print("cloud_maybe:", cloud_maybe)
        maybe_config = get_secure_share_cloud_config(interactive=True, cloud=cloud_maybe)
    elif config is not None:
        console.print(Panel(f"📄 Loading configuration from: {config}", width=150, border_style="blue"))
        maybe_config = Args.from_config(absolute(config))
    else:
        maybe_config = None

    if maybe_config is not None:
        if args.zip == ArgsDefaults.zip_:
            args.zip = maybe_config.zip
        if args.encrypt == ArgsDefaults.encrypt:
            args.encrypt = maybe_config.encrypt
        if args.share == ArgsDefaults.share:
            args.share = maybe_config.share
        if args.root == ArgsDefaults.root:
            args.root = maybe_config.root
        if args.rel2home == ArgsDefaults.rel2home:
            args.rel2home = maybe_config.rel2home
        if args.pwd == ArgsDefaults.pwd:
            args.pwd = maybe_config.pwd
        if args.os_specific == ArgsDefaults.os_specific:
            args.os_specific = maybe_config.os_specific

    root = args.root
    rel2home = args.rel2home
    pwd = args.pwd
    encrypt = args.encrypt
    zip_arg = args.zip
    share = args.share
    os_specific = args.os_specific

    if source.startswith(":"):  # default cloud name is omitted cloud_name:  # or ES in source
        # At the moment, this cloud.json defaults overrides the args and is activated only when source or target are just ":"
        # consider activating it by a flag, and also not not overriding explicitly passed args options.
        assert ES not in target, "Not Implemented here yet."
        path = absolute(target)
        if maybe_config is None:
            tmp_maybe_config: Optional[Args] = find_cloud_config(path=path)
            maybe_config = tmp_maybe_config

        if maybe_config is None:
            default_cloud: str = read_ini(DEFAULTS_PATH)["general"]["rclone_config_name"]
            console.print(Panel(f"⚠️  No cloud config found. Using default cloud: {default_cloud}", width=150, border_style="yellow"))
            source = default_cloud + ":" + source[1:]
        else:
            tmp = maybe_config
            source = f"{tmp.cloud}:" + source[1:]
            root = tmp.root
            rel2home = tmp.rel2home
            pwd = tmp.pwd
            encrypt = tmp.encrypt
            zip_arg = tmp.zip
            share = tmp.share

    if target.startswith(":"):  # default cloud name is omitted cloud_name:  # or ES in target
        assert ES not in source, "Not Implemented here yet."
        path = absolute(source)
        if maybe_config is None:
            maybe_config = find_cloud_config(path)

        if maybe_config is None:
            default_cloud = read_ini(DEFAULTS_PATH)["general"]["rclone_config_name"]
            console.print(Panel(f"⚠️  No cloud config found. Using default cloud: {default_cloud}", width=150, border_style="yellow"))
            target = default_cloud + ":" + target[1:]
            print("target mutated to:", target, f"because of default cloud being {default_cloud}")
        else:
            tmp = maybe_config
            # print("target mutated to:", target, f"because of cloud config being {tmp.cloud}")
            target = f"{tmp.cloud}:" + target[1:]
            root = tmp.root
            rel2home = tmp.rel2home
            pwd = tmp.pwd
            encrypt = tmp.encrypt
            zip_arg = tmp.zip
            share = tmp.share

    if ":" in source and (source[1] != ":" if len(source) > 1 else True):  # avoid the deceptive case of "C:/"
        source_parts: list[str] = source.split(":")
        cloud = source_parts[0]

        if len(source_parts) > 1 and source_parts[1] == ES:  # the source path is to be inferred from target.
            assert ES not in target, f"You can't use expand symbol `{ES}` in both source and target. Cyclical inference dependency arised."
            target_obj = absolute(target)
            from machineconfig.utils.path_extended import PathExtended

            remote_path = PathExtended(target_obj).get_remote_path(os_specific=os_specific, root=root, rel2home=rel2home, strict=False)
            source = f"{cloud}:{remote_path.as_posix()}"
        else:  # source path is mentioned, target? maybe.
            if target == ES:  # target path is to be inferred from source.
                raise NotImplementedError("There is no .get_local_path method yet")
            else:
                target_obj = absolute(target)
        if zip_arg and ".zip" not in source:
            source += ".zip"
        if encrypt and ".enc" not in source:
            source += ".enc"

    elif ":" in target and (target[1] != ":" if len(target) > 1 else True):  # avoid the case of "C:/"
        target_parts: list[str] = target.split(":")
        cloud = target.split(":")[0]
        if len(target_parts) > 1 and target_parts[1] == ES:  # the target path is to be inferred from source.
            assert ES not in source, "You can't use $ in both source and target. Cyclical inference dependency arised."
            source_obj = absolute(source)
            from machineconfig.utils.path_extended import PathExtended

            remote_path = PathExtended(source_obj).get_remote_path(os_specific=os_specific, root=root, rel2home=rel2home, strict=False)
            target = f"{cloud}:{remote_path.as_posix()}"
        else:  # target path is mentioned, source? maybe.
            target = str(target)
            if source == ES:
                raise NotImplementedError("There is no .get_local_path method yet")
            else:
                source_obj = absolute(source)
        if zip_arg and ".zip" not in target:
            target += ".zip"
        if encrypt and ".enc" not in target:
            target += ".enc"
    else:
        console.print(Panel("❌ ERROR: Invalid path configuration\nEither source or target must be a remote path (i.e. machine:path)", title="[bold red]Error[/bold red]", border_style="red"))
        raise ValueError(f"Either source or target must be a remote path (i.e. machine:path)\nGot: source: `{source}`, target: `{target}`")

    console.print(Panel("🔍 Path resolution complete", title="[bold blue]Resolution[/bold blue]", border_style="blue"))
    pprint({"cloud": cloud, "source": str(source), "target": str(target)}, "CLI Resolution")
    _ = pwd, encrypt, zip_arg, share
    return cloud, str(source), str(target)
