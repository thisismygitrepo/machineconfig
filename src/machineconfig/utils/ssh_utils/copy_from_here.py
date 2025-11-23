

from typing import Optional
from pathlib import Path
from machineconfig.utils.accessories import randstr
from machineconfig.utils.meta import lambda_to_python_script
from machineconfig.utils.ssh_utils.abc import DEFAULT_PICKLE_SUBDIR
from machineconfig.utils.code import get_uv_command


def copy_from_here(
    self: "SSH", source_path: str, target_rel2home: Optional[str], compress_with_zip: bool, recursive: bool, overwrite_existing: bool
) -> None:
    if self.sftp is None:
        raise RuntimeError(f"SFTP connection not available for {self.hostname}. Cannot transfer files.")
    source_obj = Path(source_path).expanduser().absolute()
    if not source_obj.exists():
        raise RuntimeError(f"SSH Error: source `{source_obj}` does not exist!")
    if target_rel2home is None:
        try:
            target_rel2home = str(source_obj.relative_to(Path.home()))
        except ValueError:
            raise RuntimeError(f"If target is not specified, source must be relative to home directory, but got: {source_obj}")
    if not compress_with_zip and source_obj.is_dir():
        if not recursive:
            raise RuntimeError(
                f"SSH Error: source `{source_obj}` is a directory! Set `recursive=True` for recursive sending or `compress_with_zip=True` to zip it first."
            )
        file_paths_to_upload: list[Path] = [file_path for file_path in source_obj.rglob("*") if file_path.is_file()]
        self.create_parent_dir_and_check_if_exists(path_rel2home=target_rel2home, overwrite_existing=overwrite_existing)
        for idx, file_path in enumerate(file_paths_to_upload):
            print(f"   {idx + 1:03d}. {file_path}")
        for file_path in file_paths_to_upload:
            remote_file_target = Path(target_rel2home).joinpath(file_path.relative_to(source_obj))
            self.copy_from_here(
                source_path=str(file_path),
                target_rel2home=str(remote_file_target),
                compress_with_zip=False,
                recursive=False,
                overwrite_existing=overwrite_existing,
            )
        return None
    if compress_with_zip:
        print("🗜️ ZIPPING ...")
        import shutil

        zip_path = Path(str(source_obj) + "_archive")
        if source_obj.is_dir():
            shutil.make_archive(str(zip_path), "zip", source_obj)
        else:
            shutil.make_archive(str(zip_path), "zip", source_obj.parent, source_obj.name)
        source_obj = Path(str(zip_path) + ".zip")
        if not target_rel2home.endswith(".zip"):
            target_rel2home = target_rel2home + ".zip"
    if Path(target_rel2home).parent.as_posix() not in {"", "."}:
        self.create_parent_dir_and_check_if_exists(path_rel2home=target_rel2home, overwrite_existing=overwrite_existing)
    print(f"""📤 [SFTP UPLOAD] Sending file: {repr(source_obj)}  ==>  Remote Path: {target_rel2home}""")
    try:
        with self.tqdm_wrap(ascii=True, unit="b", unit_scale=True) as pbar:
            if self.sftp is None:  # type: ignore[unreachable]
                raise RuntimeError(f"SFTP connection lost for {self.hostname}")
            print(f"Uploading {source_obj} to\n{Path(self.remote_specs['home_dir']).joinpath(target_rel2home)}")
            self.sftp.put(
                localpath=str(source_obj), remotepath=str(Path(self.remote_specs["home_dir"]).joinpath(target_rel2home)), callback=pbar.view_bar
            )
    except Exception:
        if compress_with_zip and source_obj.exists() and str(source_obj).endswith("_archive.zip"):
            source_obj.unlink()
        raise

    if compress_with_zip:

        def unzip_archive(zip_file_path: str, overwrite_flag: bool) -> None:
            from pathlib import Path
            import shutil
            import zipfile

            archive_path = Path(zip_file_path).expanduser()
            extraction_directory = archive_path.parent / archive_path.stem
            if overwrite_flag and extraction_directory.exists():
                shutil.rmtree(extraction_directory)
            with zipfile.ZipFile(archive_path, "r") as archive_handle:
                archive_handle.extractall(extraction_directory)
            archive_path.unlink()

        command = lambda_to_python_script(
            lambda: unzip_archive(
                zip_file_path=str(Path(self.remote_specs["home_dir"]).joinpath(target_rel2home)), overwrite_flag=overwrite_existing
            ),
            in_global=True,
            import_module=False,
        )
        tmp_py_file = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/create_target_dir_{randstr()}.py")
        tmp_py_file.parent.mkdir(parents=True, exist_ok=True)
        tmp_py_file.write_text(command, encoding="utf-8")
        remote_tmp_py = tmp_py_file.relative_to(Path.home()).as_posix()
        self.copy_from_here(source_path=str(tmp_py_file), target_rel2home=None, compress_with_zip=False, recursive=False, overwrite_existing=True)
        self.run_shell_cmd_on_remote(
            command=f"""{get_uv_command(platform=self.remote_specs['system'])} run python {remote_tmp_py}""",
            verbose_output=False,
            description=f"UNZIPPING {target_rel2home}",
            strict_stderr=True,
            strict_return_code=True,
        )
        source_obj.unlink()
        tmp_py_file.unlink(missing_ok=True)
    return None


if __name__ == "__main__":
    from machineconfig.utils.ssh import SSH
