
#!/usr/bin/env python3
import base64
import pathlib
import pprint
import shutil
import subprocess
import tempfile
import os
from typing import Any, overload, Literal, Union

from git import Optional


def _format_preview_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    return pprint.pformat(value, width=88, sort_dicts=True)


def _toml_inline_table(values: dict[str, str]) -> str:
    if not values:
        return ""
    parts: list[str] = []
    for key in sorted(values.keys()):
        raw_value = values[key]
        escaped = raw_value.replace("\\", "\\\\").replace('"', '\\"')
        parts.append(f'{key} = "{escaped}"')
    return "env = { " + ", ".join(parts) + " }\n"


def _normalize_extension(extension: str | None) -> str | None:
    if extension is None:
        return None
    trimmed = extension.strip()
    if trimmed.startswith("."):
        trimmed = trimmed[1:]
    if not trimmed:
        return None
    return trimmed


def _infer_extension_from_key(key: Optional[str]) -> str | None:
    if not isinstance(key, str):
        return None
    candidate = key.strip()
    if not candidate or any(char.isspace() for char in candidate):
        return None
    suffix = pathlib.Path(candidate).suffix
    if not suffix:
        return None
    return _normalize_extension(suffix)


@overload
def select_from_options(options_to_preview_mapping: dict[str, Any], extension: str | None, multi: Literal[True], preview_size_percent: float) -> list[str]: ...
@overload
def select_from_options(options_to_preview_mapping: dict[str, Any], extension: str | None, multi: Literal[False], preview_size_percent: float) -> Union[str, None]: ...
def select_from_options(options_to_preview_mapping: dict[str, Any], extension: str | None, multi: bool, preview_size_percent: float) -> Union[Union[str, None], list[str]]:
    keys = list(options_to_preview_mapping.keys())
    if not keys:
        return [] if multi else None
    normalized_extension = _normalize_extension(extension)
    preview_panel_size = max(10, min(90, int(preview_size_percent)))
    terminal_width = shutil.get_terminal_size(fallback=(120, 40)).columns
    preview_width = max(20, int(terminal_width * preview_panel_size / 100) - 4)
    with tempfile.TemporaryDirectory(prefix="tv_channel_") as tmpdir:
        tempdir = pathlib.Path(tmpdir)
        entries: list[str] = []
        index_map: dict[int, str] = {}
        preview_map_path = tempdir / "previews.tsv"
        preview_rows: list[str] = []
        for idx, key in enumerate(keys):
            display_key = key.replace("\t", "    ").replace("\n", " ")
            entries.append(f"{idx}\t{display_key}")
            index_map[idx] = key
            preview_value = _format_preview_value(options_to_preview_mapping[key])
            encoded_preview = base64.b64encode(preview_value.encode("utf-8")).decode("ascii")
            entry_extension = normalized_extension or _infer_extension_from_key(key) or ""
            preview_rows.append(f"{idx}\t{encoded_preview}\t{entry_extension}")
        preview_map_path.write_text("\n".join(preview_rows), encoding="utf-8")
        entries_path = tempdir / "entries.tsv"
        entries_path.write_text("\n".join(entries), encoding="utf-8")
        preview_script = tempdir / "preview.sh"
        preview_script.write_text(
            """#!/usr/bin/env bash
set -euo pipefail

idx="$1"
script_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
previews_file="${script_dir}/previews.tsv"

if [[ ! -f "${previews_file}" ]]; then
    exit 0
fi

encoded_preview="$(awk -F '\t' -v idx="${idx}" '($1==idx){print $2; exit}' "${previews_file}" || true)"

if [[ -z "${encoded_preview}" ]]; then
    exit 0
fi

preview_content="$(printf '%s' "${encoded_preview}" | base64 --decode)"

preview_ext_from_row="$(awk -F '\t' -v idx="${idx}" '($1==idx){print $3; exit}' "${previews_file}" || true)"
preview_ext="${MCFG_PREVIEW_EXT:-${preview_ext_from_row}}"
preview_width="${MCFG_PREVIEW_WIDTH:-}"
preview_size_pct="${MCFG_PREVIEW_SIZE_PCT:-}"

if [[ -z "${preview_width}" && -n "${COLUMNS:-}" ]]; then
    if [[ "${preview_size_pct}" =~ ^[0-9]+$ ]]; then
        preview_width=$((COLUMNS * preview_size_pct / 100))
    else
        preview_width="${COLUMNS}"
    fi
fi

if command -v bat >/dev/null 2>&1; then
    bat_args=(--force-colorization --style=plain --paging=never --wrap=character)
    if [[ -n "${preview_ext}" ]]; then
        bat_args+=(--language "${preview_ext}")
    fi
    if [[ "${preview_width}" =~ ^[0-9]+$ ]]; then
        bat_args+=(--terminal-width "${preview_width}")
    fi
    printf '%s' "${preview_content}" | bat "${bat_args[@]}"
elif command -v glow >/dev/null 2>&1; then
    printf '%s' "${preview_content}" | glow -
elif command -v fold >/dev/null 2>&1 && [[ "${preview_width}" =~ ^[0-9]+$ ]]; then
    printf '%s' "${preview_content}" | fold -s -w "${preview_width}"
else
    printf '%s' "${preview_content}"
fi
""",
            encoding="utf-8"
        )
        preview_script.chmod(0o755)
        preview_env: dict[str, str] = {
            "BAT_THEME": "ansi",
            "MCFG_PREVIEW_SIZE_PCT": str(preview_panel_size),
        }
        if normalized_extension is not None:
            preview_env["MCFG_PREVIEW_EXT"] = normalized_extension
        if preview_width > 0:
            preview_env["MCFG_PREVIEW_WIDTH"] = str(preview_width)
        preview_env_line = _toml_inline_table(preview_env)
        channel_config = f"""[metadata]
name = "temp_options"
description = "Temporary channel for selecting options"

[source]
command = "bat '{entries_path}'"
display = "{{split:\\t:1}}"
output = "{{split:\\t:0}}"

[preview]
command = "{preview_script} {{split:\\t:0}}"
{preview_env_line}

[ui.preview_panel]
size = {preview_panel_size}
"""
        channel_path = tempdir / "temp_options.toml"
        channel_path.write_text(channel_config, encoding="utf-8")
        env = os.environ.copy()
        tv_config_dir = pathlib.Path.home() / ".config" / "television"
        if not tv_config_dir.exists():
            tv_config_dir = pathlib.Path(os.getenv("XDG_CONFIG_HOME", str(pathlib.Path.home() / ".config"))) / "television"
        cable_dir = tv_config_dir / "cable"
        cable_dir.mkdir(parents=True, exist_ok=True)
        temp_channel_link = cable_dir / "temp_options.toml"
        if temp_channel_link.exists() or temp_channel_link.is_symlink():
            temp_channel_link.unlink()
        temp_channel_link.symlink_to(channel_path)
        output_file = tempdir / "selection.txt"
        try:
            result = subprocess.run(["tv", "temp_options"], check=False, stdout=output_file.open("w"), text=True, env=env)
        finally:
            if temp_channel_link.exists() or temp_channel_link.is_symlink():
                temp_channel_link.unlink()
        if result.returncode not in (0, 130):
            raise SystemExit(result.returncode)
        if result.returncode == 130:
            return [] if multi else None
        if not output_file.exists():
            return [] if multi else None
        selected_lines = [line.strip() for line in output_file.read_text().splitlines() if line.strip()]
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


if __name__ == "__main__":
    demo_mapping: dict[str, str] = {
        "Option 1": "# Option 1\nThis is the preview for option 1.",
        "Option 2": "# Option 2\nThis is the preview for option 2.",
        "Option 3": "# Option 3\nThis is the preview for option 3."
    }
    result = select_from_options(demo_mapping, multi=True, extension="md", preview_size_percent=50)
    print(f"Selected: {result}")
