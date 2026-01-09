#!/usr/bin/env python3
import base64
import pathlib
import pprint
import shutil
import subprocess
import tempfile
import os
from typing import Any, Optional


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


def main(options_to_preview_mapping: dict[str, Any], extension: str | None = None) -> str | None:
    keys = list(options_to_preview_mapping.keys())
    if not keys:
        return None
    normalized_extension = _normalize_extension(extension)
    preview_panel_size = 50
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
        preview_script = tempdir / "preview.ps1"
        preview_script_content = r'''param([string]$idx)
$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$previewsFile = Join-Path $scriptDir 'previews.tsv'
if (-not (Test-Path $previewsFile)) { exit 0 }
$lines = Get-Content -Path $previewsFile -Encoding UTF8
$encodedPreview = ''
$previewExtFromRow = ''
foreach ($line in $lines) {
    $parts = $line -split "`t"
    if ($parts.Count -ge 2 -and $parts[0] -eq $idx) {
        $encodedPreview = $parts[1]
        if ($parts.Count -ge 3) { $previewExtFromRow = $parts[2] }
        break
    }
}
if ([string]::IsNullOrEmpty($encodedPreview)) { exit 0 }
$previewBytes = [System.Convert]::FromBase64String($encodedPreview)
$previewContent = [System.Text.Encoding]::UTF8.GetString($previewBytes)
$previewExt = if ($env:MCFG_PREVIEW_EXT) { $env:MCFG_PREVIEW_EXT } else { $previewExtFromRow }
$previewWidth = $env:MCFG_PREVIEW_WIDTH
$previewSizePct = $env:MCFG_PREVIEW_SIZE_PCT
if ([string]::IsNullOrEmpty($previewWidth) -and $Host.UI.RawUI.WindowSize.Width) {
    $cols = $Host.UI.RawUI.WindowSize.Width
    if ($previewSizePct -match '^\d+$') {
        $previewWidth = [int]($cols * [int]$previewSizePct / 100)
    } else {
        $previewWidth = $cols
    }
}
$batPath = Get-Command bat -ErrorAction SilentlyContinue
if ($batPath) {
    $batArgs = @('--force-colorization', '--style=plain', '--paging=never', '--wrap=character')
    if (-not [string]::IsNullOrEmpty($previewExt)) { $batArgs += @('--language', $previewExt) }
    if ($previewWidth -match '^\d+$') { $batArgs += @('--terminal-width', $previewWidth) }
    $previewContent | & bat @batArgs
} elseif (Get-Command glow -ErrorAction SilentlyContinue) {
    $previewContent | & glow -
} else {
    Write-Output $previewContent
}
'''
        preview_script.write_text(preview_script_content, encoding="utf-8")
        env = os.environ.copy()
        env["BAT_THEME"] = "ansi"
        env["MCFG_PREVIEW_SIZE_PCT"] = str(preview_panel_size)
        if normalized_extension is not None:
            env["MCFG_PREVIEW_EXT"] = normalized_extension
        if preview_width > 0:
            env["MCFG_PREVIEW_WIDTH"] = str(preview_width)
        entries_path_escaped = str(entries_path).replace("\\", "/")
        preview_script_escaped = str(preview_script).replace("\\", "/")
        source_cmd = f"bat --style=plain --paging=never '{entries_path_escaped}'"
        preview_cmd = f"pwsh -NoProfile -ExecutionPolicy Bypass -File '{preview_script_escaped}' {{split:\t:0}}"
        tv_args = [
            "tv",
            "--source-command", source_cmd,
            "--source-display", "{split:\t:1}",
            "--source-output", "{split:\t:0}",
            "--preview-command", preview_cmd,
            "--preview-size", str(preview_panel_size),
            "--no-remote",
        ]
        result = subprocess.run(tv_args, check=False, capture_output=True, text=True, env=env)
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
    result = main(demo_mapping)
    print(f"Selected: {result}")
