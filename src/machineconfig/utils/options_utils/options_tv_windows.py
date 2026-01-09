#!/usr/bin/env python3
import pathlib
import pprint
import shutil
from typing import Any


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


def main(options_to_preview_mapping: dict[str, Any], extension: str | None = None, multi: bool = False) -> str | list[str] | None:
    keys = list(options_to_preview_mapping.keys())
    if not keys:
        return [] if multi else None
    normalized_extension = _normalize_extension(extension)
    preview_panel_size = 50
    from machineconfig.utils.accessories import randstr
    tempdir = pathlib.Path.home() / "tmp_results" / "tmp_files" / f"tv_channel_{randstr(6)}"
    tempdir.mkdir(parents=True, exist_ok=True)
    try:
        entries: list[str] = []
        index_map: dict[int, str] = {}
        ext_for_preview = normalized_extension or "txt"
        for idx, key in enumerate(keys):
            display_key = key.replace("\t", "    ").replace("\n", " ")
            entries.append(f"{idx}\t{display_key}")
            index_map[idx] = key
            preview_value = _format_preview_value(options_to_preview_mapping[key])
            preview_file = tempdir / f"preview_{idx}.{ext_for_preview}"
            preview_file.write_text(preview_value, encoding="utf-8")
        entries_path = tempdir / "entries.tsv"
        entries_path.write_text("\n".join(entries), encoding="utf-8")
        output_file = tempdir / "selection.txt"
        output_file_str = str(output_file)
        preview_script = tempdir / "preview.cmd"
        tempdir_win = str(tempdir)
        preview_script.write_text(f"""@echo off
bat --force-colorization --style=plain --paging=never "{tempdir_win}\\preview_%1.{ext_for_preview}"
""", encoding="utf-8")
        source_cmd = f"cmd /C type \"{entries_path}\""
        preview_cmd = str(preview_script) + " {split:\\t:0}"
        tv_cmd = f'''$OutputEncoding = [Console]::InputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
tv --ansi --source-command '{source_cmd}' --source-display "{{split:\\t:1}}" --source-output "{{split:\\t:0}}" --preview-command "{preview_cmd}" --preview-size {preview_panel_size} --no-remote | Out-File -Encoding utf8 -FilePath "{output_file_str}"
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
            try:
                index = int(line)
                key = index_map.get(index)
                if key is not None:
                    selected_keys.append(key)
            except ValueError:
                continue
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
    result = main(demo_mapping, multi=True)
    print(f"Selected: {result}")
