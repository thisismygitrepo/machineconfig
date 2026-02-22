from __future__ import annotations

from pathlib import Path
from platform import system
import os
import subprocess
import sys
import time
from typing import Any, Callable, Literal, Optional, TypeAlias

from machineconfig.utils.accessories import randstr
from machineconfig.utils.io import decrypt as io_decrypt
from machineconfig.utils.io import encrypt as io_encrypt
from machineconfig.utils.path_extended import FILE_MODE, timestamp, validate_name

PathPredicate: TypeAlias = Callable[[Path], bool]
PathLike: TypeAlias = Path | str | None


def _to_path(path: Path | str) -> Path:
    return path if isinstance(path, Path) else Path(path)


def _expand(path: Path | str) -> Path:
    return _to_path(path).expanduser()


def _safe_resolve(path: Path, strict: bool = False) -> Path:
    try:
        return path.resolve(strict=strict)
    except OSError:
        return path


def _is_user_admin() -> bool:
    if os.name == "nt":
        try:
            return __import__("ctypes").windll.shell32.IsUserAnAdmin()
        except Exception:  # noqa: BLE001
            import traceback

            traceback.print_exc()
            print("Admin check failed, assuming not an admin.")
            return False
    return os.getuid() == 0


def _run_shell_command(
    command: str,
    shell_name: str,
    *,
    stdout: Optional[int] = subprocess.PIPE,
    stderr: Optional[int] = subprocess.PIPE,
    stdin: Optional[int] = None,
    check: bool = False,
) -> subprocess.CompletedProcess[str]:
    if shell_name in {"powershell", "pwsh"} and sys.platform == "win32":
        args: list[str] = [shell_name, "-Command", command]
        return subprocess.run(args, check=check, text=True, stdout=stdout, stderr=stderr, stdin=stdin)
    executable = "/bin/bash" if shell_name == "bash" and sys.platform != "win32" else None
    return subprocess.run(command, check=check, text=True, stdout=stdout, stderr=stderr, stdin=stdin, shell=True, executable=executable)


def _append_text(path: Path, text: str) -> Path:
    return Path(f"{path}{text}")


def _print_message(message: str) -> None:
    try:
        print(message)
    except UnicodeEncodeError:
        print("P._return warning: UnicodeEncodeError, could not print message.")


def _path_from_parts(parts: tuple[str, ...] | list[str]) -> Path:
    return Path(*parts) if len(parts) else Path("")


def _resolve_path(path: Path, folder: PathLike, name: Optional[str], target_path: PathLike, default_name: str, rel2it: bool = False) -> Path:
    if target_path is not None:
        resolved = _to_path(target_path)
        if rel2it:
            resolved = path.joinpath(resolved)
        resolved = _safe_resolve(_expand(resolved))
        assert folder is None and name is None, "If `path` is passed, `folder` and `name` cannot be passed."
        assert not resolved.is_dir(), f"`path` passed is a directory! pass it with `folder` kwarg. `{resolved}`"
        return resolved
    final_name = default_name if name is None else str(name)
    final_folder = path.parent if folder is None else _to_path(folder)
    if rel2it:
        final_folder = path.joinpath(final_folder)
    return _safe_resolve(_expand(final_folder)) / final_name


def _finalize_result(source: Path, result: Path, *, inplace: bool, orig: bool, verbose: bool, message: str) -> Path:
    delayed_message = ""
    if inplace:
        delete(source, sure=True, verbose=False)
        delayed_message = f"DELETED 🗑️❌ {source!r}."
    if verbose:
        _print_message(message)
    if verbose and delayed_message != "":
        _print_message(delayed_message)
    return source if orig else result


def delete(path: Path, sure: bool = False, verbose: bool = True) -> Path:
    path_obj = _to_path(path)
    if not sure:
        if verbose:
            _print_message(f"❌ Did NOT DELETE because user is not sure. file: {path_obj!r}.")
        return path_obj
    expanded = _expand(path_obj)
    if not expanded.exists():
        expanded.unlink(missing_ok=True)
        if verbose:
            _print_message(f"❌ Could NOT DELETE nonexisting file {expanded!r}. ")
        return path_obj
    if expanded.is_file() or expanded.is_symlink():
        expanded.unlink(missing_ok=True)
    else:
        import shutil

        shutil.rmtree(expanded, ignore_errors=False)
    if verbose:
        _print_message(f"🗑️ ❌ DELETED {expanded!r}.")
    return path_obj


def move(
    path: Path,
    folder: Optional[Path] = None,
    name: Optional[str] = None,
    target_path: Optional[Path] = None,
    rel2it: bool = False,
    overwrite: bool = False,
    verbose: bool = True,
    parents: bool = True,
    content: bool = False,
) -> Path:
    path_obj = _to_path(path)
    source = _safe_resolve(_expand(path_obj))
    destination = _resolve_path(source, folder=folder, name=name, target_path=target_path, default_name=source.absolute().name, rel2it=rel2it)
    if parents:
        destination.parent.mkdir(parents=True, exist_ok=True)
    if content:
        assert source.is_dir(), NotADirectoryError(f"💥 When `content` is True path must be a directory. It is not: `{source!r}`")
        for child in source.glob("*"):
            move(path=child, folder=destination.parent, content=False, overwrite=overwrite, verbose=verbose)
        return destination
    if overwrite:
        tmp_path = source.rename(destination.parent.absolute() / randstr())
        delete(destination, sure=True, verbose=verbose)
        tmp_path.rename(destination)
    else:
        try:
            source.rename(destination)
        except OSError as err:
            import shutil

            shutil.move(str(source), str(destination))
            _ = err
    if verbose:
        _print_message(f"🚚 MOVED {path_obj!r} ==> {destination!r}`")
    return destination


def copy(
    path: Path,
    folder: Optional[Path] = None,
    name: Optional[str] = None,
    target_path: Optional[Path] = None,
    content: bool = False,
    verbose: bool = True,
    append_name: Optional[str] = None,
    overwrite: bool = False,
    orig: bool = False,
) -> Path:
    path_obj = _to_path(path)
    source = _safe_resolve(_expand(path_obj))
    destination = _safe_resolve(_expand(_resolve_path(source, folder=folder, name=name, target_path=target_path, default_name=source.name, rel2it=False)))
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination == source:
        destination = append(path_obj, name=append_name if append_name is not None else f"_copy_{randstr()}")
    if not content and overwrite and destination.exists():
        delete(destination, sure=True)
    if not content and not overwrite and destination.exists():
        raise FileExistsError(f"💥 Destination already exists: {destination!r}")
    if source.is_file():
        import shutil

        shutil.copy(str(source), str(destination))
        if verbose:
            _print_message(f"🖨️ COPIED {source!r} ==> {destination!r}")
    elif source.is_dir():
        destination = destination.parent if content else destination
        from shutil import copytree

        copytree(str(source), str(destination))
        if verbose:
            _print_message(f"🖨️ COPIED {'Content of ' if content else ''} {source!r} ==> {destination!r}")
    else:
        _print_message(f"💥 Could NOT COPY. Not a file nor a path: {source!r}.")
    return path_obj if orig else destination


def download(
    url_path: Path,
    folder: Optional[Path] = None,
    name: Optional[str] = None,
    allow_redirects: bool = True,
    timeout: Optional[int] = None,
    params: Any = None,
) -> Path:
    import requests

    response = requests.get(as_url_str(url_path), allow_redirects=allow_redirects, timeout=timeout, params=params)
    assert response.status_code == 200, f"Download failed with status code {response.status_code}\n{response.text}"
    if name is not None:
        filename = name
    else:
        try:
            filename = response.headers["Content-Disposition"].split("filename=")[1].replace('"', "")
        except (KeyError, IndexError):
            src_url = response.history[-1].url if len(response.history) > 0 else response.url
            filename = validate_name(str(Path(src_url).name))
    destination = (Path.home() / "Downloads" if folder is None else _to_path(folder)).joinpath(filename)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(response.content)
    return destination


def append(
    path: Path,
    name: str = "",
    index: bool = False,
    suffix: Optional[str] = None,
    verbose: bool = True,
    inplace: bool = False,
    overwrite: bool = False,
    orig: bool = False,
    strict: bool = True,
) -> Path:
    path_obj = _to_path(path)
    if index:
        pattern = f"*{path_obj.name.split('.')[0]}*"
        indexed_name = f"{name}_{len(search(path_obj.parent, pattern=pattern))}"
        return append(path_obj, name=indexed_name, index=False, verbose=verbose, suffix=suffix, inplace=inplace, overwrite=overwrite, orig=orig, strict=strict)
    full_name = name or ("_" + str(timestamp()))
    full_suffix = suffix or "".join(path_obj.suffixes)
    subpath = path_obj.name.split(".")[0] + full_name + full_suffix
    destination = path_obj.parent.joinpath(subpath)
    if inplace:
        assert path_obj.exists(), f"`inplace` flag is only relevant if path exists. It doesn't {path_obj}"
        if overwrite and destination.exists():
            delete(destination, sure=True, verbose=verbose)
        if not overwrite and destination.exists():
            if strict:
                raise FileExistsError(f"❌ RENAMING failed. File `{destination}` already exists.")
            if verbose:
                _print_message(f"⚠️ SKIPPED RENAMING {path_obj!r} ➡️ {destination!r} because FileExistsError and scrict=False policy.")
            return path_obj if orig else destination
        path_obj.rename(destination)
        if verbose:
            _print_message(f"RENAMED {path_obj!r} ➡️ {destination!r}")
    return path_obj if orig else destination


def with_name(
    path: Path,
    name: str,
    verbose: bool = True,
    inplace: bool = False,
    overwrite: bool = False,
    orig: bool = False,
    strict: bool = True,
) -> Path:
    path_obj = _to_path(path)
    destination = path_obj.parent / name
    if inplace:
        assert path_obj.exists(), f"`inplace` flag is only relevant if path exists. It doesn't {path_obj}"
        if overwrite and destination.exists():
            delete(destination, sure=True, verbose=verbose)
        if not overwrite and destination.exists():
            if strict:
                raise FileExistsError(f"❌ RENAMING failed. File `{destination}` already exists.")
            if verbose:
                _print_message(f"⚠️ SKIPPED RENAMING {path_obj!r} ➡️ {destination!r} because FileExistsError and scrict=False policy.")
            return path_obj if orig else destination
        path_obj.rename(destination)
        if verbose:
            _print_message(f"RENAMED {path_obj!r} ➡️ {destination!r}")
    return path_obj if orig else destination


def rel2home(path: Path) -> Path:
    return _expand(path).absolute().relative_to(Path.home())


def collapseuser(path: Path, strict: bool = True, placeholder: str = "~") -> Path:
    path_obj = _to_path(path)
    home_obj = Path.home()
    expanded = _expand(path_obj).absolute()
    if strict:
        assert str(expanded.resolve(strict=True)).startswith(str(home_obj)), ValueError(f"`{home_obj}` is not in the subpath of `{path_obj}`")
    resolved = expanded.resolve(strict=strict) if strict else _safe_resolve(expanded, strict=False)
    if str(path_obj).startswith(placeholder) or home_obj.as_posix() not in _safe_resolve(expanded, strict=False).as_posix():
        return path_obj
    return Path(placeholder) / resolved.relative_to(home_obj)


def split(
    path: Path,
    at: Optional[str] = None,
    index: Optional[int] = None,
    sep: Literal[-1, 0, 1] = 1,
    strict: bool = True,
) -> tuple[Path, Path]:
    path_obj = _to_path(path)
    if index is None and at is not None:
        if not strict:
            items = str(path_obj).split(sep=str(at))
            one, two = items[0], items[1]
            left = Path(one[:-1]) if one.endswith("/") else Path(one)
            right = Path(two[1:]) if two.startswith("/") else Path(two)
        else:
            split_index = path_obj.parts.index(str(at))
            left, right = _path_from_parts(path_obj.parts[0:split_index]), _path_from_parts(path_obj.parts[split_index + 1 :])
    elif index is not None and at is None:
        left, right = _path_from_parts(path_obj.parts[:index]), _path_from_parts(path_obj.parts[index + 1 :])
        at = path_obj.parts[index]
    else:
        raise ValueError("Either `index` or `at` can be provided. Both are not allowed simulatanesouly.")
    if sep == 0:
        return left, right
    if sep == 1:
        return left, Path(at) / right
    if sep == -1:
        return left / str(at), right
    raise ValueError(f"`sep` should take a value from the set [-1, 0, 1] but got {sep}")


def size(path: Path, units: Literal["b", "kb", "mb", "gb"] = "mb") -> float:
    path_obj = _to_path(path)
    total_size = path_obj.stat().st_size if path_obj.is_file() else sum([item.stat().st_size for item in path_obj.rglob("*") if item.is_file()])
    scale: int
    match units:
        case "b":
            scale = 1024**0
        case "kb":
            scale = 1024**1
        case "mb":
            scale = 1024**2
        case "gb":
            scale = 1024**3
    return round(number=total_size / scale, ndigits=1)


def clickable(path: Path) -> Path:
    return Path(_safe_resolve(_expand(path), strict=False).as_uri())


def as_url_str(path: Path) -> str:
    return _to_path(path).as_posix().replace("https:/", "https://").replace("http:/", "http://")


def as_zip_path(path: Path) -> Any:
    import zipfile

    return zipfile.Path(_safe_resolve(_expand(path), strict=False))


def symlink_to(path: Path, target: Path, verbose: bool = True, overwrite: bool = False, orig: bool = False, strict: bool = True) -> Path:
    path_obj = _to_path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    target_obj = _safe_resolve(_expand(target), strict=False)
    if strict:
        assert target_obj.exists(), f"Target path `{target}` (aka `{target_obj}`) doesn't exist. This will create a broken link."
    if overwrite and (path_obj.is_symlink() or path_obj.exists()):
        delete(path_obj, sure=True, verbose=verbose)
    if system() == "Windows" and not _is_user_admin():
        import win32com.shell.shell  # type: ignore

        _process_info = win32com.shell.shell.ShellExecuteEx(lpVerb="runas", lpFile=sys.executable, lpParameters=f" -c \"from pathlib import Path; Path(r'{_expand(path_obj)}').symlink_to(r'{target_obj}')\"")
        _ = _process_info
        time.sleep(1)
    else:
        _expand(path_obj).symlink_to(str(target_obj))
    if verbose:
        _print_message(f"LINKED {path_obj!r} ➡️ {target_obj!r}")
    return path_obj if orig else target_obj


def search(
    path: Path,
    pattern: str = "*",
    r: bool = False,
    files: bool = True,
    folders: bool = True,
    compressed: bool = False,
    dotfiles: bool = False,
    filters_total: Optional[list[PathPredicate]] = None,
    not_in: Optional[list[str]] = None,
    exts: Optional[list[str]] = None,
    win_order: bool = False,
) -> list[Path]:
    if isinstance(not_in, list):
        filters_notin: list[PathPredicate] = [lambda x: all([str(a_not_in) not in str(x) for a_not_in in not_in])]
    else:
        filters_notin = []
    if isinstance(exts, list):
        filters_extension: list[PathPredicate] = [lambda x: any([ext in x.name for ext in exts])]
    else:
        filters_extension = []
    active_filters = (filters_total or []) + filters_notin + filters_extension
    if not files:
        active_filters.append(lambda x: x.is_dir())
    if not folders:
        active_filters.append(lambda x: x.is_file())
    path_obj = _safe_resolve(_expand(path), strict=False)
    if ".zip" in str(path_obj) and compressed:
        import fnmatch
        import zipfile

        root = as_zip_path(path_obj)
        if not r:
            raw_zip = list(root.iterdir())
        else:
            raw_zip = [root.joinpath(item) for item in zipfile.ZipFile(str(path_obj)).namelist()]
        filtered = [item for item in raw_zip if fnmatch.fnmatch(item.at, pattern)]
        return [Path(str(item)) for item in filtered if (folders or item.is_file()) and (files or item.is_dir())]
    if dotfiles:
        raw_paths: list[Path | str] = list(path_obj.glob(pattern) if not r else path_obj.rglob(pattern))
    else:
        from glob import glob

        if r:
            globbed = glob(str(path_obj / "**" / pattern), recursive=True)
        else:
            globbed = glob(str(path_obj.joinpath(pattern)))
        raw_paths = [Path(item) for item in globbed]
    if ".zip" not in str(path_obj) and compressed:
        nested: list[Path] = []
        for compressed_file in search(path_obj, "*.zip", r=r):
            nested.extend(
                search(
                    path=compressed_file,
                    pattern=pattern,
                    r=r,
                    files=files,
                    folders=folders,
                    compressed=True,
                    dotfiles=dotfiles,
                    filters_total=active_filters,
                    not_in=not_in,
                    win_order=win_order,
                )
            )
        raw_paths = raw_paths + nested
    processed: list[Path] = []
    for item in raw_paths:
        candidate = item if isinstance(item, Path) else Path(item)
        if all([afilter(candidate) for afilter in active_filters]):
            processed.append(candidate)
    if not win_order:
        return list(processed)
    import re

    processed.sort(key=lambda x: [int(chunk) if chunk.isdigit() else chunk for chunk in re.split("([0-9]+)", string=x.stem)])
    return list(processed)


def tmpdir(prefix: str = "") -> Path:
    folder = f"tmp_dirs/{prefix + ('_' if prefix != '' else '') + randstr()}"
    return tmp(folder=Path(folder))


def tmpfile(name: Optional[str] = None, suffix: str = "", folder: Optional[Path] = None, tstamp: bool = False, noun: bool = False) -> Path:
    concrete_name = name or randstr(noun=noun)
    suffix_part = ("_" + str(timestamp())) if tstamp else ""
    folder_path = folder or Path("tmp_files")
    return tmp(file=f"{concrete_name}_{randstr()}{suffix_part}{suffix}", folder=folder_path)


def tmp(folder: Optional[Path] = None, file: Optional[str] = None, root: str = "~/tmp_results") -> Path:
    folder_path = "" if folder is None else _to_path(folder)
    file_path = "" if file is None else file
    base = Path(root).expanduser().joinpath(folder_path).joinpath(file_path)
    target_path = base.parent if file else base
    target_path.mkdir(parents=True, exist_ok=True)
    return base


def zip_path(
    path: Path,
    target_path: Optional[Path] = None,
    folder: Optional[Path] = None,
    name: Optional[str] = None,
    arcname: Optional[str] = None,
    inplace: bool = False,
    verbose: bool = True,
    content: bool = False,
    orig: bool = False,
    mode: FILE_MODE = "w",
    **kwargs: Any,
) -> Path:
    source = _safe_resolve(_expand(path), strict=False)
    output_path = _safe_resolve(_expand(_resolve_path(source, folder, name, target_path, source.name)), strict=False)
    arcname_obj = Path(arcname or source.name)
    if arcname_obj.name != source.name:
        arcname_obj = arcname_obj / source.name
    if source.is_file():
        import zipfile

        op_zip = output_path if output_path.suffix == ".zip" else _append_text(output_path, ".zip")
        with zipfile.ZipFile(str(op_zip), mode=mode) as zip_handle:
            zip_handle.write(filename=str(source), arcname=str(arcname_obj), compress_type=zipfile.ZIP_DEFLATED, **kwargs)
        output_path = Path(op_zip)
    else:
        import shutil

        if content:
            root_dir, base_dir = source, "."
        else:
            root_dir, base_dir = split(source, at=str(arcname_obj.parts[0]), sep=1)[0], str(arcname_obj)
        base_name = str(output_path)[:-4] if str(output_path).endswith(".zip") else str(output_path)
        output_path = Path(shutil.make_archive(base_name=base_name, format="zip", root_dir=str(root_dir), base_dir=str(base_dir), verbose=False, **kwargs))
    message = f"ZIPPED {source!r} ==> {output_path!r}"
    return _finalize_result(_to_path(path), output_path, inplace=inplace, orig=orig, verbose=verbose, message=message)


def _unzip_archive(
    path: Path,
    folder: Optional[Path] = None,
    target_path: Optional[Path] = None,
    name: Optional[str] = None,
    verbose: bool = True,
    content: bool = False,
    inplace: bool = False,
    overwrite: bool = False,
    orig: bool = False,
    pwd: Optional[str] = None,
    tmp: bool = False,
    pattern: Optional[str] = None,
    merge: bool = False,
) -> Path:
    _ = pwd, pattern
    assert merge is False, "I have not implemented this yet"
    assert target_path is None, "I have not implemented this yet"
    if tmp:
        tmp_root = Path("~/tmp_results").expanduser()
        tmp_root.mkdir(parents=True, exist_ok=True)
        return _unzip_archive(path, folder=tmp_root.joinpath("tmp_unzips").joinpath(randstr()), content=True).joinpath(_to_path(path).stem)
    source = zipfile_path = _safe_resolve(_expand(path), strict=False)
    if any(ztype in str(source.parent) for ztype in (".zip", ".7z")):
        matches = [item for item in (".zip", ".7z", "") if item in str(source)]
        ztype = matches[0]
        if ztype == "":
            return source
        marker = next(item for item in source.parts if ztype in item)
        zipfile_path, name_part = split(source, at=str(marker), sep=-1)
        name = str(name_part)
    output_folder = (zipfile_path.parent / zipfile_path.stem) if folder is None else _safe_resolve(_expand(folder), strict=False).joinpath(zipfile_path.stem)
    output_folder = output_folder if not content else output_folder.parent
    if source.suffix == ".7z":
        raise NotImplementedError("I have not implemented this yet")
    if overwrite:
        if not content:
            output_folder.joinpath(name or "").mkdir(parents=True, exist_ok=True)
            delete(output_folder.joinpath(name or ""), sure=True, verbose=True)
        else:
            import zipfile

            entries = [x for x in zipfile.ZipFile(str(path)).namelist() if "/" not in x or (len(x.split("/")) == 2 and x.endswith("/"))]
            for item in entries:
                delete(output_folder.joinpath(name or "", item.replace("/", "")), sure=True, verbose=True)
    import zipfile

    target_name = None if name is None else Path(name).as_posix()
    with zipfile.ZipFile(str(zipfile_path), "r") as zip_obj:
        if target_name is None:
            zip_obj.extractall(str(output_folder))
            result = Path(str(output_folder))
        else:
            zip_obj.extract(member=str(target_name), path=str(output_folder))
            result = Path(str(output_folder)) / target_name
    message = f"UNZIPPED {zipfile_path!r} ==> {result!r}"
    return _finalize_result(_to_path(path), Path(result), inplace=inplace, orig=orig, verbose=verbose, message=message)


def unzip(
    path: Path,
    folder: Optional[Path] = None,
    target_path: Optional[Path] = None,
    name: Optional[str] = None,
    verbose: bool = True,
    content: bool = False,
    inplace: bool = False,
    overwrite: bool = False,
    orig: bool = False,
    pwd: Optional[str] = None,
    tmp: bool = False,
    pattern: Optional[str] = None,
    merge: bool = False,
) -> Path:
    return _unzip_archive(
        path=path,
        folder=folder,
        target_path=target_path,
        name=name,
        verbose=verbose,
        content=content,
        inplace=inplace,
        overwrite=overwrite,
        orig=orig,
        pwd=pwd,
        tmp=tmp,
        pattern=pattern,
        merge=merge,
    )


def untar(path: Path, folder: Optional[Path] = None, name: Optional[str] = None, target_path: Optional[Path] = None, inplace: bool = False, orig: bool = False, verbose: bool = True) -> Path:
    output_path = _safe_resolve(_expand(_resolve_path(_to_path(path), folder, name, target_path, _to_path(path).name.replace(".tar", ""))), strict=False)
    import tarfile

    with tarfile.open(str(_safe_resolve(_expand(path), strict=False)), "r") as tar_obj:
        tar_obj.extractall(path=str(output_path))
    message = f"UNTARRED {_to_path(path)!r} ==>  {output_path!r}"
    return _finalize_result(_to_path(path), output_path, inplace=inplace, orig=orig, verbose=verbose, message=message)


def ungz(path: Path, folder: Optional[Path] = None, name: Optional[str] = None, target_path: Optional[Path] = None, inplace: bool = False, orig: bool = False, verbose: bool = True) -> Path:
    output_path = _safe_resolve(_expand(_resolve_path(_to_path(path), folder, name, target_path, _to_path(path).name.replace(".gz", ""))), strict=False)
    import gzip

    output_path.write_bytes(gzip.decompress(_safe_resolve(_expand(path), strict=False).read_bytes()))
    message = f"UNGZED {_to_path(path)!r} ==>  {output_path!r}"
    return _finalize_result(_to_path(path), output_path, inplace=inplace, orig=orig, verbose=verbose, message=message)


def unxz(path: Path, folder: Optional[Path] = None, name: Optional[str] = None, target_path: Optional[Path] = None, inplace: bool = False, orig: bool = False, verbose: bool = True) -> Path:
    output_path = _safe_resolve(_expand(_resolve_path(_to_path(path), folder, name, target_path, _to_path(path).name.replace(".xz", ""))), strict=False)
    import lzma

    output_path.write_bytes(lzma.decompress(_safe_resolve(_expand(path), strict=False).read_bytes()))
    message = f"UNXZED {_to_path(path)!r} ==>  {output_path!r}"
    return _finalize_result(_to_path(path), output_path, inplace=inplace, orig=orig, verbose=verbose, message=message)


def unbz(path: Path, folder: Optional[Path] = None, name: Optional[str] = None, target_path: Optional[Path] = None, inplace: bool = False, orig: bool = False, verbose: bool = True) -> Path:
    default_name = _to_path(path).name.replace(".bz", "").replace(".tbz", ".tar")
    output_path = _safe_resolve(_expand(_resolve_path(_to_path(path), folder, name, target_path, default_name)), strict=False)
    import bz2

    output_path.write_bytes(bz2.decompress(_safe_resolve(_expand(path), strict=False).read_bytes()))
    message = f"UNBZED {_to_path(path)!r} ==>  {output_path!r}"
    return _finalize_result(_to_path(path), output_path, inplace=inplace, orig=orig, verbose=verbose, message=message)


def decompress(path: Path, folder: Optional[Path] = None, name: Optional[str] = None, target_path: Optional[Path] = None, inplace: bool = False, orig: bool = False, verbose: bool = True) -> Path:
    path_obj = _to_path(path)
    path_str = str(path_obj)
    if path_str.endswith(".tar.gz") or path_str.endswith(".tgz"):
        return untar(ungz(path_obj, name=f"tmp_{randstr()}.tar", inplace=inplace), folder=folder, name=name, target_path=target_path, inplace=True, orig=orig, verbose=verbose)
    if path_str.endswith(".tar"):
        return untar(path_obj, folder=folder, name=name, target_path=target_path, inplace=inplace, orig=orig, verbose=verbose)
    if path_str.endswith(".gz"):
        return ungz(path_obj, folder=folder, name=name, target_path=target_path, inplace=inplace, verbose=verbose, orig=orig)
    if path_str.endswith(".tar.bz") or path_str.endswith(".tbz") or path_str.endswith(".tar.bz2"):
        return untar(unbz(path_obj, name=f"tmp_{randstr()}.tar", inplace=inplace), folder=folder, name=name, target_path=target_path, inplace=True, orig=orig, verbose=verbose)
    if path_str.endswith(".tar.xz"):
        return untar(unxz(path_obj, inplace=inplace), folder=folder, name=name, target_path=target_path, inplace=True, orig=orig, verbose=verbose)
    if path_str.endswith(".zip"):
        return unzip(path_obj, folder=folder, target_path=target_path, name=name, inplace=inplace, verbose=verbose, orig=orig)
    if path_str.endswith(".7z"):
        import tempfile
        import py7zr  # type: ignore

        archive_path = _to_path(path_obj)
        if not archive_path.is_file():
            raise FileNotFoundError(f"Archive file not found: {archive_path!r}")
        destination = Path(tempfile.mkdtemp(prefix=f"unzip7z_{archive_path.stem}_"))
        with py7zr.SevenZipFile(str(archive_path), mode="r") as archive:
            archive.extractall(path=str(destination))
        return destination
    raise ValueError(f"Cannot decompress file with unknown extension: {path_obj}")


def _encrypt_path(
    path: Path,
    key: Optional[bytes] = None,
    pwd: Optional[str] = None,
    folder: Optional[Path] = None,
    name: Optional[str] = None,
    target_path: Optional[Path] = None,
    verbose: bool = True,
    suffix: str = ".enc",
    inplace: bool = False,
    orig: bool = False,
) -> Path:
    source = _safe_resolve(_expand(path), strict=False)
    output_path = _resolve_path(source, folder, name, target_path, source.name + suffix)
    assert source.is_file(), f"Cannot encrypt a directory. You might want to try `zip_n_encrypt`. {path}"
    output_path.write_bytes(io_encrypt(msg=source.read_bytes(), key=key, pwd=pwd))
    message = f"🔒🔑 ENCRYPTED: {source!r} ==> {output_path!r}."
    return _finalize_result(_to_path(path), output_path, inplace=inplace, orig=orig, verbose=verbose, message=message)


def encrypt(
    path: Path,
    key: Optional[bytes] = None,
    pwd: Optional[str] = None,
    folder: Optional[Path] = None,
    name: Optional[str] = None,
    target_path: Optional[Path] = None,
    verbose: bool = True,
    suffix: str = ".enc",
    inplace: bool = False,
    orig: bool = False,
) -> Path:
    return _encrypt_path(path=path, key=key, pwd=pwd, folder=folder, name=name, target_path=target_path, verbose=verbose, suffix=suffix, inplace=inplace, orig=orig)


def _decrypt_path(
    path: Path,
    key: Optional[bytes] = None,
    pwd: Optional[str] = None,
    target_path: Optional[Path] = None,
    folder: Optional[Path] = None,
    name: Optional[str] = None,
    verbose: bool = True,
    suffix: str = ".enc",
    inplace: bool = False,
) -> Path:
    source = _safe_resolve(_expand(path), strict=False)
    default_name = source.name.replace(suffix, "") if suffix in source.name else "decrypted_" + source.name
    output_path = _resolve_path(source, folder=folder, name=name, target_path=target_path, default_name=default_name)
    output_path.write_bytes(io_decrypt(token=source.read_bytes(), key=key, pwd=pwd))
    message = f"🔓🔑 DECRYPTED: {source!r} ==> {output_path!r}."
    delayed_message = ""
    if inplace:
        delete(_to_path(path), sure=True, verbose=False)
        delayed_message = f"DELETED 🗑️❌ {_to_path(path)!r}."
    if verbose:
        _print_message(message)
    if verbose and delayed_message != "":
        _print_message(delayed_message)
    return output_path


def decrypt(
    path: Path,
    key: Optional[bytes] = None,
    pwd: Optional[str] = None,
    target_path: Optional[Path] = None,
    folder: Optional[Path] = None,
    name: Optional[str] = None,
    verbose: bool = True,
    suffix: str = ".enc",
    inplace: bool = False,
) -> Path:
    return _decrypt_path(path=path, key=key, pwd=pwd, target_path=target_path, folder=folder, name=name, verbose=verbose, suffix=suffix, inplace=inplace)


def zip_n_encrypt(path: Path, key: Optional[bytes] = None, pwd: Optional[str] = None, inplace: bool = False, verbose: bool = True, orig: bool = False, content: bool = False) -> Path:
    path_obj = _to_path(path)
    return _encrypt_path(zip_path(path_obj, inplace=inplace, verbose=verbose, content=content), key=key, pwd=pwd, verbose=verbose, inplace=True) if not orig else path_obj


def decrypt_n_unzip(path: Path, key: Optional[bytes] = None, pwd: Optional[str] = None, inplace: bool = False, verbose: bool = True, orig: bool = False) -> Path:
    path_obj = _to_path(path)
    return _unzip_archive(_decrypt_path(path_obj, key=key, pwd=pwd, verbose=verbose, inplace=inplace), folder=None, inplace=True, content=False) if not orig else path_obj


def get_remote_path(path: Path, root: Optional[str], os_specific: bool = False, rel2home: bool = True, strict: bool = True) -> Path:
    import platform

    os_part = platform.system().lower() if os_specific else "generic_os"
    path_obj = _to_path(path)
    if not rel2home:
        reduced = path_obj
    else:
        try:
            reduced = _expand(path_obj).absolute().relative_to(Path.home())
        except ValueError as err:
            if strict:
                raise err
            reduced = path_obj
    if isinstance(root, str):
        part1 = reduced.parts[0] if len(reduced.parts) else ""
        if part1 == "/":
            sanitized = _path_from_parts(list(reduced.parts[1:])).as_posix()
        else:
            sanitized = reduced.as_posix()
        return Path(f"{root}/{os_part}/{sanitized}")
    return Path(os_part) / reduced


def to_cloud(
    path: Path,
    cloud: str,
    remotepath: Optional[Path] = None,
    zip: bool = False,
    encrypt: bool = False,
    key: Optional[bytes] = None,
    pwd: Optional[str] = None,
    rel2home: bool = False,
    strict: bool = True,
    share: bool = False,
    verbose: bool = True,
    os_specific: bool = False,
    transfers: int = 10,
    root: Optional[str] = "myhome",
) -> Path:
    _ = transfers
    source_path = _to_path(path)
    temporary: list[Path] = []
    localpath = source_path.expanduser().absolute() if not source_path.exists() else source_path
    if zip:
        localpath = zip_path(localpath, inplace=False)
        temporary.append(localpath)
    if encrypt:
        localpath = _encrypt_path(localpath, key=key, pwd=pwd, inplace=False)
        temporary.append(localpath)
    if remotepath is None:
        remote_obj = get_remote_path(localpath, root=root, os_specific=os_specific, rel2home=rel2home, strict=strict)
    else:
        remote_obj = _to_path(remotepath)
    from rclone_python import rclone

    if verbose:
        _print_message(f"⬆️ UPLOADING {localpath!r} TO {cloud}:{remote_obj.as_posix()}`")
    rclone.copyto(in_path=localpath.as_posix(), out_path=f"{cloud}:{remote_obj.as_posix()}")
    for item in temporary:
        delete(item, sure=True)
    if verbose:
        _print_message(f"{'⬆️' * 5} UPLOAD COMPLETED.")
    if share:
        if verbose:
            _print_message("🔗 SHARING FILE")
        shell_to_use = "powershell" if sys.platform == "win32" else "bash"
        command = f"rclone link '{cloud}:{remote_obj.as_posix()}'"
        completed = _run_shell_command(command, shell_to_use)
        from machineconfig.utils.terminal import Response

        res = Response.from_completed_process(completed).capture()
        maybe_link = res.op2path(strict_err=False, strict_returncode=False)
        if maybe_link is None:
            res.print()
            raise RuntimeError(f"💥 Could not get link for {source_path}.")
        res.print_if_unsuccessful(desc="Cloud Storage Operation", strict_err=True, strict_returncode=True)
        return Path(str(maybe_link))
    return source_path


def from_cloud(
    path: Path,
    cloud: str,
    remotepath: Optional[Path] = None,
    decrypt: bool = False,
    unzip: bool = False,
    key: Optional[bytes] = None,
    pwd: Optional[str] = None,
    rel2home: bool = False,
    os_specific: bool = False,
    strict: bool = True,
    transfers: int = 10,
    root: Optional[str] = "myhome",
    verbose: bool = True,
    overwrite: bool = True,
    merge: bool = False,
) -> Path | None:
    _ = verbose, transfers
    source_path = _to_path(path)
    if remotepath is None:
        remote_obj = get_remote_path(source_path, root=root, os_specific=os_specific, rel2home=rel2home, strict=strict)
        remote_obj = _append_text(remote_obj, ".zip") if unzip else remote_obj
        remote_obj = _append_text(remote_obj, ".enc") if decrypt else remote_obj
    else:
        remote_obj = _to_path(remotepath)
    localpath = source_path.expanduser().absolute()
    localpath = _append_text(localpath, ".zip") if unzip else localpath
    localpath = _append_text(localpath, ".enc") if decrypt else localpath
    from rclone_python import rclone

    try:
        rclone.copyto(in_path=f"{cloud}:{remote_obj.as_posix()}", out_path=localpath.as_posix())
    except Exception as err:  # noqa: BLE001
        _print_message(f"to_cloud error {err}")
        return None
    if decrypt:
        localpath = _decrypt_path(localpath, key=key, pwd=pwd, inplace=True)
    if unzip:
        localpath = _unzip_archive(localpath, inplace=True, verbose=True, overwrite=overwrite, content=True, merge=merge)
    return localpath


def sync_to_cloud(
    path: Path,
    cloud: str,
    sync_up: bool = False,
    sync_down: bool = False,
    os_specific: bool = False,
    rel2home: bool = True,
    transfers: int = 10,
    delete: bool = False,
    root: Optional[str] = "myhome",
    verbose: bool = True,
) -> Path | None:
    source_path = _to_path(path)
    tmp_path_obj = source_path.expanduser().absolute()
    tmp_path_obj.parent.mkdir(parents=True, exist_ok=True)
    local_path, remote_rel = tmp_path_obj.as_posix(), get_remote_path(source_path, root=root, os_specific=os_specific).as_posix()
    if sync_up:
        source, target = local_path, f"{cloud}:{remote_rel if rel2home else local_path}"
    else:
        source, target = f"{cloud}:{remote_rel if rel2home else local_path}", local_path
    if not sync_down and not sync_up:
        if verbose:
            _print_message(f"SYNCING 🔄️ {source} {'<>' * 7} {target}`")
        rclone_cmd = f"""rclone bisync '{source}' '{target}' --resync --remove-empty-dirs """
    else:
        _print_message(f"SYNCING 🔄️ {source} {'>' * 15} {target}`")
        rclone_cmd = f"""rclone sync '{source}' '{target}' """
    rclone_cmd += f" --progress --transfers={transfers} --verbose"
    rclone_cmd += " --delete-during" if delete else ""
    if verbose:
        _print_message(rclone_cmd)
    stdout_target: Optional[int] = None if verbose else subprocess.PIPE
    stderr_target: Optional[int] = None if verbose else subprocess.PIPE
    shell_to_use = "powershell" if sys.platform == "win32" else "bash"
    completed = _run_shell_command(rclone_cmd, shell_to_use, stdout=stdout_target, stderr=stderr_target)
    from machineconfig.utils.terminal import Response

    response = Response.from_completed_process(completed)
    success = response.is_successful(strict_err=False, strict_returcode=True)
    if not success:
        response.print(capture=False, desc="Cloud Storage Operation")
        return None
    return source_path


__all__ = [
    "as_url_str",
    "as_zip_path",
    "append",
    "clickable",
    "collapseuser",
    "copy",
    "decompress",
    "decrypt",
    "decrypt_n_unzip",
    "delete",
    "download",
    "encrypt",
    "from_cloud",
    "get_remote_path",
    "move",
    "rel2home",
    "search",
    "size",
    "split",
    "symlink_to",
    "sync_to_cloud",
    "timestamp",
    "tmp",
    "tmpdir",
    "tmpfile",
    "to_cloud",
    "unbz",
    "ungz",
    "untar",
    "unxz",
    "unzip",
    "validate_name",
    "with_name",
    "zip_n_encrypt",
    "zip_path",
]
