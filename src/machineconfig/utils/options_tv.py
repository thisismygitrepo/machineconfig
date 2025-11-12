

#!/usr/bin/env python3
import pathlib
import shlex
import subprocess
import tempfile


def _safe_filename(key: str, index: int) -> str:
    base = f"{index:04d}_" + "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in key)
    if not base.strip("_"):
        base = f"{index:04d}_option"
    return f"{base}.md"


def main(options_to_preview_mapping: dict[str, str]) -> str | None:
    keys = list(options_to_preview_mapping.keys())
    if not keys:
        return None
    with tempfile.TemporaryDirectory(prefix="tv_md_") as tmpdir:
        tempdir = pathlib.Path(tmpdir)
        entries: list[str] = []
        index_map: dict[int, str] = {}
        for idx, key in enumerate(keys):
            fname = _safe_filename(key, idx)
            fpath = tempdir / fname
            fpath.write_text(options_to_preview_mapping[key], encoding="utf-8")
            display_key = key.replace("\t", " ").replace("\n", " ")
            entries.append(f"{idx}\t{display_key}\t{fpath}")
            index_map[idx] = key
        entries_path = tempdir / "entries.tsv"
        entries_path.write_text("\n".join(entries), encoding="utf-8")
        tv_cmd = [
            "tv",
            "--source-command",
            f"cat {shlex.quote(str(entries_path))}",
            "--source-entry-delimiter",
            "\t",
            "--source-display",
            "{1}",
            "--source-output",
            "{0}",
            "--preview-command",
            "bat -n --color=always {2}",
            "--preview-size",
            "50"
        ]
        result = subprocess.run(tv_cmd, check=False, capture_output=True, text=True)
        if result.returncode not in (0, 130):
            raise SystemExit(result.returncode)
        if result.returncode == 130:
            return None
        selected = result.stdout.strip()
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
