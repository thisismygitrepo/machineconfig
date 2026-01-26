from machineconfig.scripts.python.helpers.helpers_cloud.cloud_helpers import absolute, find_cloud_config, get_secure_share_cloud_config
from machineconfig.utils.ve import CLOUD
from machineconfig.utils.io import read_ini
from machineconfig.utils.source_of_truth import DEFAULTS_PATH
from machineconfig.utils.accessories import pprint
from typing import Optional, cast
from rich.console import Console
from rich.panel import Panel


ES = "^"  # chosen carefully to not mean anything on any shell. `$` was a bad choice.
console = Console()


def parse_cloud_source_target(
         cloud_config_explicit: CLOUD,
         cloud_config_defaults: CLOUD,
         cloud_config_name: Optional[str],
         source: str, target: str
         ) -> tuple[str, str, str]:
    print("Source:", source)
    print("Target:", target)

    # Step 1: find the third config if any
    cloud_config_from_name: Optional[CLOUD] = None
    if cloud_config_name is not None:
        if cloud_config_name == "ss":
            cloud_maybe: Optional[str] = target.split(":")[0]
            if cloud_maybe == "": cloud_maybe = None
            print("cloud_maybe:", cloud_maybe)
            cloud_config_from_name = get_secure_share_cloud_config(interactive=True, cloud=cloud_maybe)
        else:
            config_path = absolute(cloud_config_name)
            console.print(Panel(f"📄 Loading configuration from: {cloud_config_name}", width=150, border_style="blue"))
            if config_path.exists():
                cloud_config_from_name = find_cloud_config(config_path)
                if cloud_config_from_name is None:
                    raise FileNotFoundError(f"Configuration file at {cloud_config_name} has no [cloud] section.")
            else:
                raise FileNotFoundError(f"Configuration passed is not a valid known config name nor a valid config file path: {cloud_config_name}")

    else:
        cloud_config_from_name = None

    # step 2: solve for missing cloud names in source/target if any
    if source.startswith(":") and cloud_config_from_name is None:  # cloud name is omitted, needs to be inferred from config file.
        if ES in target:
            raise NotImplementedError("Not Implemented here yet.")
        target_local_path = absolute(target)  # if source is remote, target must be local, against which we can search for .ve.yaml
        cloud_config_from_name = find_cloud_config(path=target_local_path)
        if cloud_config_from_name is None:  # last resort, use default cloud (user didn't pass cloud name, didn't pass config file)
            default_cloud: str = read_ini(DEFAULTS_PATH)["general"]["rclone_config_name"]
            console.print(Panel(f"⚠️  No cloud config found. Using default cloud: {default_cloud}", width=150, border_style="yellow"))
            source = default_cloud + ":" + source[1:]
        else:
            source = cloud_config_from_name["cloud"] + ":" + source[1:]
    if target.startswith(":"):  # default cloud name is omitted cloud_name:  # or ES in target
        if ES in source:
            raise NotImplementedError("Not Implemented here yet.")
        source_local_path = absolute(source)
        if cloud_config_from_name is None: cloud_config_from_name = find_cloud_config(source_local_path)
        if cloud_config_from_name is None:
            default_cloud = read_ini(DEFAULTS_PATH)["general"]["rclone_config_name"]
            console.print(Panel(f"⚠️  No cloud config found. Using default cloud: {default_cloud}", width=150, border_style="yellow"))
            target = default_cloud + ":" + target[1:]
            print("target mutated to:", target, f"because of default cloud being {default_cloud}")
        else:
            target = cloud_config_from_name['cloud'] + ":" + target[1:]

    cloud_config_final: CLOUD
    if cloud_config_from_name is None:
        cloud_config_final = cloud_config_explicit
    else:
        cloud_config_final = cloud_config_from_name
        override_keys = {
            k: (cloud_config_explicit[k], cloud_config_defaults[k]) for k in cloud_config_explicit.keys() & cloud_config_defaults.keys() if cloud_config_explicit[k] != cloud_config_defaults[k]}  # type: ignore
        tmp = dict(cloud_config_final)
        tmp.update(override_keys)
        cloud_config_final = cast(CLOUD, tmp)

    if ":" in source and (source[1] != ":" if len(source) > 1 else True):  # avoid the deceptive case of "C:/"
        source_parts: list[str] = source.split(":")
        cloud = source_parts[0]
        if len(source_parts) > 1 and source_parts[1] == ES:  # the source path is to be inferred from target.
            assert ES not in target, f"You can't use expand symbol `{ES}` in both source and target. Cyclical inference dependency arised."
            target_obj = absolute(target)
            from machineconfig.utils.path_extended import PathExtended
            remote_path = PathExtended(target_obj).get_remote_path(os_specific=cloud_config_final["os_specific"], root=cloud_config_final["root"], rel2home=cloud_config_final["rel2home"], strict=False)
            source = f"{cloud}:{remote_path.as_posix()}"
        else:  # source path is mentioned, target? maybe.
            if target == ES:  # target path is to be inferred from source.
                raise NotImplementedError("There is no .get_local_path method yet")
            else:
                target_obj = absolute(target)
        if cloud_config_final["zip"] and ".zip" not in source:
            source += ".zip"
        if cloud_config_final["encrypt"] and ".enc" not in source:
            source += ".enc"
    elif ":" in target and (target[1] != ":" if len(target) > 1 else True):  # avoid the case of "C:/"
        target_parts: list[str] = target.split(":")
        cloud = target.split(":")[0]
        if len(target_parts) > 1 and target_parts[1] == ES:  # the target path is to be inferred from source.
            assert ES not in source, "You can't use $ in both source and target. Cyclical inference dependency arised."
            source_obj = absolute(source)
            from machineconfig.utils.path_extended import PathExtended
            remote_path = PathExtended(source_obj).get_remote_path(os_specific=cloud_config_final["os_specific"], root=cloud_config_final["root"], rel2home=cloud_config_final["rel2home"], strict=False)
            target = f"{cloud}:{remote_path.as_posix()}"
        else:  # target path is mentioned, source? maybe.
            target = str(target)
            if source == ES:
                raise NotImplementedError("There is no .get_local_path method yet")
            else:
                source_obj = absolute(source)
        if cloud_config_final["zip"] and ".zip" not in target:
            target += ".zip"
        if cloud_config_final["encrypt"] and ".enc" not in target:
            target += ".enc"
    else:
        console.print(Panel("❌ ERROR: Invalid path configuration\nEither source or target must be a remote path (i.e. machine:path)", title="[bold red]Error[/bold red]", border_style="red"))
        raise ValueError(f"Either source or target must be a remote path (i.e. machine:path)\nGot: source: `{source}`, target: `{target}`")
    console.print(Panel("🔍 Path resolution complete", title="[bold blue]Resolution[/bold blue]", border_style="blue"))
    pprint({"cloud": cloud, "source": str(source), "target": str(target)}, "CLI Resolution")
    return cloud, str(source), str(target)
