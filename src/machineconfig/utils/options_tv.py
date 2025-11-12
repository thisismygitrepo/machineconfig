

#!/usr/bin/env python3
import base64
import pathlib
import subprocess
import tempfile
import os


def main(options_to_preview_mapping: dict[str, str]) -> str | None:
    keys = list(options_to_preview_mapping.keys())
    if not keys:
        return None
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
            encoded_preview = base64.b64encode(options_to_preview_mapping[key].encode("utf-8")).decode("ascii")
            preview_rows.append(f"{idx}\t{encoded_preview}")
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

if command -v bat >/dev/null 2>&1; then
    printf '%s' "${preview_content}" | glow -
elif command -v bat >/dev/null 2>&1; then
    printf '%s' "${preview_content}" | bat --language=markdown --color=always --style=plain --paging=never
elif command -v glow >/dev/null 2>&1; then
    printf '%s' "${preview_content}" | glow -
else
    printf '%s' "${preview_content}"
fi
""",
            encoding="utf-8"
        )
        preview_script.chmod(0o755)
        channel_config = f"""[metadata]
name = "temp_options"
description = "Temporary channel for selecting options"

[source]
command = "cat '{entries_path}'"
display = "{{split:\\t:1}}"
output = "{{split:\\t:0}}"

[preview]
command = "{preview_script} {{split:\\t:0}}"

[ui.preview_panel]
size = 50
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
            return None
        if not output_file.exists():
            return None
        selected = output_file.read_text().strip()
        if not selected:
            return None
        try:
            index = int(selected)
        except ValueError:
            return None
        return index_map.get(index)


if __name__ == "__main__":
    demo_mapping = {
        "Option 1": "# Option 1\nThis is the preview for option 1.",
        "Option 2": "# Option 2\nThis is the preview for option 2.",
        "Option 3": "# Option 3\nThis is the preview for option 3."
    }
    main(demo_mapping)
