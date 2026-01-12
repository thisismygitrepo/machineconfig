#!/usr/bin/env python3
import pathlib
import pprint
import shutil
from typing import Any, Literal, Union, overload


def _format_preview_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    return pprint.pformat(value, width=88, sort_dicts=True)


def _normalize_extension(extension: str | None) -> str | None:
    if extension is None:
        return None
    trimmed = extension.strip()
    if trimmed.startswith("."):
        trimmed = trimmed[1:]
    if not trimmed:
        return None
    return trimmed


@overload
def select_from_options(options_to_preview_mapping: dict[str, Any], extension: str | None, multi: Literal[True], preview_size_percent: float) -> list[str]: ...
@overload
def select_from_options(options_to_preview_mapping: dict[str, Any], extension: str | None, multi: Literal[False], preview_size_percent: float) -> str | None: ...
def select_from_options(options_to_preview_mapping: dict[str, Any], extension: str | None, multi: bool, preview_size_percent: float) -> Union[list[str], Union[str, None]]:
    keys = list(options_to_preview_mapping.keys())
    if not keys:
        return [] if multi else None
    normalized_extension = _normalize_extension(extension)
    preview_panel_size = max(10, min(90, int(preview_size_percent)))
    from machineconfig.utils.accessories import randstr
    tempdir = pathlib.Path.home() / "tmp_results" / "tmp_files" / f"tv_channel_{randstr(6)}"
    tempdir.mkdir(parents=True, exist_ok=True)
    try:
        index_map: dict[str, str] = {}
        ext_for_preview = normalized_extension or "txt"
        entries_lines: list[str] = []
        for idx, key in enumerate(keys):
            display_key = key.replace("\n", " ")
            entries_lines.append(f"{idx}|{display_key}")
            index_map[str(idx)] = key
            preview_value = _format_preview_value(options_to_preview_mapping[key])
            preview_file = tempdir / f"{idx}.{ext_for_preview}"
            preview_file.write_text(preview_value, encoding="utf-8")
        entries_path = tempdir / "entries.txt"
        entries_path.write_text("\n".join(entries_lines), encoding="utf-8")
        output_file = tempdir / "selection.txt"
        tempdir_fwd = str(tempdir).replace("\\", "/")
        source_cmd = f"cmd /C type \"{entries_path}\""
        preview_cmd = f"bat --force-colorization --style=plain --paging=never {tempdir_fwd}/{{split:|:0}}.{ext_for_preview}"
        tv_cmd = f'''$OutputEncoding = [Console]::InputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
tv --ansi --source-command '{source_cmd}' --source-display '{{split:|:1}}' --source-output '{{split:|:0}}' --preview-command '{preview_cmd}' --preview-size {preview_panel_size} --no-remote | Out-File -Encoding utf8 -FilePath "{output_file}"
'''
        from machineconfig.utils.code import run_shell_script
        result = run_shell_script(tv_cmd, display_script=False, clean_env=False)
        if result.returncode not in (0, 130) and not output_file.exists():
            raise SystemExit(result.returncode)
        if result.returncode == 130:
            return [] if multi else None
        if not output_file.exists():
            return [] if multi else None
        selected_lines = [line.strip() for line in output_file.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        if not selected_lines:
            return [] if multi else None
        selected_keys: list[str] = []
        for line in selected_lines:
            key = index_map.get(line)
            if key is not None:
                selected_keys.append(key)
        if multi:
            return selected_keys
        return selected_keys[0] if selected_keys else None
    finally:
        shutil.rmtree(tempdir, ignore_errors=True)


if __name__ == "__main__":
    demo_mapping: dict[str, str] = {
        "Option 1": "# Option 1\nThis is the preview for option 1.",
        "Option 2": "# Option 2\nThis is the preview for option 2.",
        "Option 3": "# Option 3\nThis is the preview for option 3."
    }
    result = select_from_options(demo_mapping, multi=True, extension="md", preview_size_percent=50)
    print(f"Selected: {result}")
