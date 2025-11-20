

from typing import Optional, Union
from pathlib import Path
from machineconfig.utils.accessories import randstr
from machineconfig.utils.meta import lambda_to_python_script
from machineconfig.utils.ssh_utils.abc import MACHINECONFIG_VERSION, DEFAULT_PICKLE_SUBDIR


def copy_to_here(
    self: "SSH",
    source: Union[str, Path],
    target: Optional[Union[str, Path]],
    compress_with_zip: bool = False,
    recursive: bool = False,
    internal_call: bool = False,
) -> None:
    if self.sftp is None:
        raise RuntimeError(f"SFTP connection not available for {self.hostname}. Cannot transfer files.")

    if not internal_call:
        print(f"{'⬇️' * 5} SFTP DOWNLOADING FROM `{source}` TO `{target}`")

    source_obj = Path(source)
    expanded_source = self.expand_remote_path(source_path=source_obj)

    if not compress_with_zip:
        is_dir = self.check_remote_is_dir(source_path=expanded_source)

        if is_dir:
            if not recursive:
                raise RuntimeError(
                    f"SSH Error: source `{source_obj}` is a directory! Set recursive=True for recursive transfer or compress_with_zip=True to zip it."
                )

            def search_files(directory_path: str, json_output_path: str) -> list[str]:
                from pathlib import Path
                import json

                file_paths_list = [
                    file_path.as_posix() for file_path in Path(directory_path).expanduser().absolute().rglob("*") if file_path.is_file()
                ]
                json_result_path = Path(json_output_path)
                json_result_path.parent.mkdir(parents=True, exist_ok=True)
                json_result_path.write_text(json.dumps(file_paths_list, indent=2), encoding="utf-8")
                print(json_result_path.as_posix())
                return file_paths_list

            remote_json_output = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/return_{randstr()}.json").as_posix()
            command = lambda_to_python_script(
                lambda: search_files(directory_path=expanded_source, json_output_path=remote_json_output),
        in_global=True, import_module=False
            )
            response = self.run_py_remotely(
                python_code=command,
                uv_with=[MACHINECONFIG_VERSION],
                uv_project_dir=None,
                description="Searching for files in source",
                verbose_output=False,
                strict_stderr=False,
                strict_return_code=False,
            )
            remote_json_path = response.op.strip()
            if not remote_json_path:
                raise RuntimeError(f"Could not resolve source path {source} - no response from remote")

            local_json = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/local_{randstr()}.json")
            self.simple_sftp_get(remote_path=remote_json_path, local_path=local_json)
            import json

            try:
                source_list_str = json.loads(local_json.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, FileNotFoundError) as err:
                raise RuntimeError(f"Could not resolve source path {source} - invalid JSON response: {err}") from err
            finally:
                if local_json.exists():
                    local_json.unlink()
            assert isinstance(source_list_str, list), f"Could not resolve source path {source}"
            file_paths_to_download = [Path(file_path_str) for file_path_str in source_list_str]

            if target is None:

                def collapse_to_home_dir(absolute_path: str, json_output_path: str) -> str:
                    from pathlib import Path
                    import json

                    source_absolute_path = Path(absolute_path).expanduser().absolute()
                    try:
                        relative_to_home = source_absolute_path.relative_to(Path.home())
                        collapsed_path_posix = (Path("~") / relative_to_home).as_posix()
                        json_result_path = Path(json_output_path)
                        json_result_path.parent.mkdir(parents=True, exist_ok=True)
                        json_result_path.write_text(json.dumps(collapsed_path_posix, indent=2), encoding="utf-8")
                        print(json_result_path.as_posix())
                        return collapsed_path_posix
                    except ValueError:
                        raise RuntimeError(f"Source path must be relative to home directory: {source_absolute_path}")

                remote_json_output = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/return_{randstr()}.json").as_posix()
                command = lambda_to_python_script(
                    lambda: collapse_to_home_dir(absolute_path=expanded_source, json_output_path=remote_json_output),
                    in_global=True,
                    import_module=False,
                )
                response = self.run_py_remotely(
                    python_code=command,
                    uv_with=[MACHINECONFIG_VERSION],
                    uv_project_dir=None,
                    description="Finding default target via relative source path",
                    verbose_output=False,
                    strict_stderr=False,
                    strict_return_code=False,
                )
                remote_json_path_dir = response.op.strip()
                if not remote_json_path_dir:
                    raise RuntimeError("Could not resolve target path - no response from remote")

                local_json_dir = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/local_{randstr()}.json")
                self.simple_sftp_get(remote_path=remote_json_path_dir, local_path=local_json_dir)
                import json

                try:
                    target_dir_str = json.loads(local_json_dir.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, FileNotFoundError) as err:
                    raise RuntimeError(f"Could not resolve target path - invalid JSON response: {err}") from err
                finally:
                    if local_json_dir.exists():
                        local_json_dir.unlink()
                assert isinstance(target_dir_str, str), "Could not resolve target path"
                target = Path(target_dir_str)

            target_dir = Path(target).expanduser().absolute()

            for idx, file_path in enumerate(file_paths_to_download):
                print(f"   {idx + 1:03d}. {file_path}")

            for file_path in file_paths_to_download:
                local_file_target = target_dir.joinpath(Path(file_path).relative_to(expanded_source))
                self.copy_to_here(source=file_path, target=local_file_target, compress_with_zip=False, recursive=False, internal_call=True)

            return None

    if compress_with_zip:
        print("🗜️ ZIPPING ...")

        def zip_source(path_to_zip: str, json_output_path: str) -> str:
            from pathlib import Path
            import shutil
            import json

            source_to_compress = Path(path_to_zip).expanduser().absolute()
            archive_base_path = source_to_compress.parent / (source_to_compress.name + "_archive")
            if source_to_compress.is_dir():
                shutil.make_archive(str(archive_base_path), "zip", source_to_compress)
            else:
                shutil.make_archive(str(archive_base_path), "zip", source_to_compress.parent, source_to_compress.name)
            zip_file_path = str(archive_base_path) + ".zip"
            json_result_path = Path(json_output_path)
            json_result_path.parent.mkdir(parents=True, exist_ok=True)
            json_result_path.write_text(json.dumps(zip_file_path, indent=2), encoding="utf-8")
            print(json_result_path.as_posix())
            return zip_file_path

        remote_json_output = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/return_{randstr()}.json").as_posix()
        command = lambda_to_python_script(
            lambda: zip_source(path_to_zip=expanded_source, json_output_path=remote_json_output),
        in_global=True, import_module=False
        )
        response = self.run_py_remotely(
            python_code=command,
            uv_with=[MACHINECONFIG_VERSION],
            uv_project_dir=None,
            description=f"Zipping source file {source}",
            verbose_output=False,
            strict_stderr=False,
            strict_return_code=False,
        )
        remote_json_path = response.op.strip()
        if not remote_json_path:
            raise RuntimeError(f"Could not zip {source} - no response from remote")

        local_json = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/local_{randstr()}.json")
        self.simple_sftp_get(remote_path=remote_json_path, local_path=local_json)
        import json

        try:
            zipped_path = json.loads(local_json.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError) as err:
            raise RuntimeError(f"Could not zip {source} - invalid JSON response: {err}") from err
        finally:
            if local_json.exists():
                local_json.unlink()
        assert isinstance(zipped_path, str), f"Could not zip {source}"
        source_obj = Path(zipped_path)
        expanded_source = zipped_path

    if target is None:

        def collapse_to_home(absolute_path: str, json_output_path: str) -> str:
            from pathlib import Path
            import json

            source_absolute_path = Path(absolute_path).expanduser().absolute()
            try:
                relative_to_home = source_absolute_path.relative_to(Path.home())
                collapsed_path_posix = (Path("~") / relative_to_home).as_posix()
                json_result_path = Path(json_output_path)
                json_result_path.parent.mkdir(parents=True, exist_ok=True)
                json_result_path.write_text(json.dumps(collapsed_path_posix, indent=2), encoding="utf-8")
                print(json_result_path.as_posix())
                return collapsed_path_posix
            except ValueError:
                raise RuntimeError(f"Source path must be relative to home directory: {source_absolute_path}")

        remote_json_output = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/return_{randstr()}.json").as_posix()
        command = lambda_to_python_script(
            lambda: collapse_to_home(absolute_path=expanded_source, json_output_path=remote_json_output),
        in_global=True, import_module=False
        )
        response = self.run_py_remotely(
            python_code=command,
            uv_with=[MACHINECONFIG_VERSION],
            uv_project_dir=None,
            description="Finding default target via relative source path",
            verbose_output=False,
            strict_stderr=False,
            strict_return_code=False,
        )
        remote_json_path = response.op.strip()
        if not remote_json_path:
            raise RuntimeError("Could not resolve target path - no response from remote")

        local_json = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/local_{randstr()}.json")
        self.simple_sftp_get(remote_path=remote_json_path, local_path=local_json)
        import json

        try:
            target_str = json.loads(local_json.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError) as err:
            raise RuntimeError(f"Could not resolve target path - invalid JSON response: {err}") from err
        finally:
            if local_json.exists():
                local_json.unlink()
        assert isinstance(target_str, str), "Could not resolve target path"
        target = Path(target_str)
        assert str(target).startswith("~"), f"If target is not specified, source must be relative to home.\n{target=}"

    target_obj = Path(target).expanduser().absolute()
    target_obj.parent.mkdir(parents=True, exist_ok=True)

    if compress_with_zip and target_obj.suffix != ".zip":
        target_obj = target_obj.with_suffix(target_obj.suffix + ".zip")

    print(f"""📥 [DOWNLOAD] Receiving: {expanded_source}  ==>  Local Path: {target_obj}""")
    try:
        with self.tqdm_wrap(ascii=True, unit="b", unit_scale=True) as pbar:
            if self.sftp is None:  # type: ignore[unreachable]
                raise RuntimeError(f"SFTP connection lost for {self.hostname}")
            self.sftp.get(remotepath=expanded_source, localpath=str(target_obj), callback=pbar.view_bar)  # type: ignore
    except Exception:
        if target_obj.exists():
            target_obj.unlink()
        raise

    if compress_with_zip:
        import zipfile

        extract_to = target_obj.parent / target_obj.stem
        with zipfile.ZipFile(target_obj, "r") as zip_ref:
            zip_ref.extractall(extract_to)
        target_obj.unlink()
        target_obj = extract_to

        def delete_temp_zip(path_to_delete: str) -> None:
            from pathlib import Path
            import shutil

            file_or_dir_path = Path(path_to_delete)
            if file_or_dir_path.exists():
                if file_or_dir_path.is_dir():
                    shutil.rmtree(file_or_dir_path)
                else:
                    file_or_dir_path.unlink()

        command = lambda_to_python_script(lambda: delete_temp_zip(path_to_delete=expanded_source),
                                in_global=True, import_module=False)
        self.run_py_remotely(
            python_code=command,
            uv_with=[MACHINECONFIG_VERSION],
            uv_project_dir=None,
            description="Cleaning temp zip files @ remote.",
            verbose_output=False,
            strict_stderr=True,
            strict_return_code=True,
        )

    print("\n")
    return None


if __name__ == "__main__":
    from machineconfig.utils.ssh import SSH

