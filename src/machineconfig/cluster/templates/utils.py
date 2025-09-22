from typing import Optional
from machineconfig.utils.path_reduced import PathExtended, PLike


def to_cloud(
    localpath: PLike,
    cloud: str,
    remotepath: Optional[PLike],
    zip: bool = False,
    encrypt: bool = False,
    key: Optional[bytes] = None,
    pwd: Optional[str] = None,
    rel2home: bool = False,
    strict: bool = True,
    # obfuscate: bool = False,
    share: bool = False,
    verbose: bool = True,
    os_specific: bool = False,
    transfers: int = 10,
    root: Optional[str] = "myhome",
) -> "PathExtended":
    to_del = []
    localpath = PathExtended(localpath).expanduser().absolute() if not PathExtended(localpath).exists() else PathExtended(localpath)
    if zip:
        localpath = localpath.zip(inplace=False)
        to_del.append(localpath)
    if encrypt:
        localpath = localpath.encrypt(key=key, pwd=pwd, inplace=False)
        to_del.append(localpath)
    if remotepath is None:
        rp = localpath.get_remote_path(root=root, os_specific=os_specific, rel2home=rel2home, strict=strict)  # if rel2home else (P(root) / localpath if root is not None else localpath)
    else:
        rp = PathExtended(remotepath)

    from rclone_python import rclone

    rclone.copy(localpath.as_posix(), f"{cloud}:{rp.as_posix()}", show_progress=True)

    if share:
        if verbose:
            print("🔗 SHARING FILE")
        tmp = rclone.link(f"{cloud}:{rp.as_posix()}")
        return PathExtended(tmp)
    return localpath


if __name__ == "__main__":
    from pathlib import Path

    localpath = Path.home().joinpath("Downloads", "exchangeInfo")
    to_cloud(localpath, "odp", remotepath=None)
