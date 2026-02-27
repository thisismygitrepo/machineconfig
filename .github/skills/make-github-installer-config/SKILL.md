---
name: make-github-installer-config
description: Create a machineconfig installer_data.json entry from a GitHub repository releases page. Use this when asked to add a new GitHub binary installer config.
---

Goal: produce one JSON object compatible with `src/machineconfig/jobs/installer/installer_data.json` and safely upsert it into the `installers` array.

Mandatory execution rule:

- Run all helper scripts with `uv run ...`.
- Never run these helpers with plain `python`.

When invoked, follow this process:

1. Read target `repoURL`, `appName`, and `doc` from the user request.
2. Scan releases and classify candidate binaries:

```bash
uv run .github/skills/make-github-installer-config/scripts/scan_github_releases.py \
  --repo-url "https://github.com/OWNER/REPO" \
  --limit 8 \
  --output ./.ai/tmp_scripts/make-github-installer-config/scan.json
```

3. Build inferred config and run latest-release presence checks:

```bash
uv run .github/skills/make-github-installer-config/scripts/build_installer_config.py \
  --repo-url "https://github.com/OWNER/REPO" \
  --app-name "appname" \
  --doc "short description" \
  --limit 8 \
  --output ./.ai/tmp_scripts/make-github-installer-config/entry.json
```

4. Verify checks from `entry.json` before writing:

- If `checks.latestPatternChecks` is non-empty, treat as warning and explain why.
- Do not silently ignore failed checks.

5. Perform a dry-run upsert first:

```bash
uv run .github/skills/make-github-installer-config/scripts/upsert_installer_data.py \
  --installer-data src/machineconfig/jobs/installer/installer_data.json \
  --entry-json ./.ai/tmp_scripts/make-github-installer-config/entry.json \
  --dry-run
```

6. If dry-run output is correct, run actual upsert:

```bash
uv run .github/skills/make-github-installer-config/scripts/upsert_installer_data.py \
  --installer-data src/machineconfig/jobs/installer/installer_data.json \
  --entry-json ./.ai/tmp_scripts/make-github-installer-config/entry.json
```

7. Validate resulting JSON file:

```bash
jq empty src/machineconfig/jobs/installer/installer_data.json
```

Output JSON entry must use this exact shape:

```json
{
  "appName": "...",
  "repoURL": "https://github.com/OWNER/REPO",
  "doc": "...",
  "fileNamePattern": {
    "amd64": {
      "linux": "... or null",
      "macos": "... or null",
      "windows": "... or null"
    },
    "arm64": {
      "linux": "... or null",
      "macos": "... or null",
      "windows": "... or null"
    }
  }
}
```

Requirements:

- If binaries are unavailable for a platform/architecture, set that value to `null`.
- Prefer Linux `musl` artifacts over `gnu` when both are available.
- Use stable, recurring filename patterns from recent releases.
- Keep `appName` lowercase and concise.
- Keep `doc` short and descriptive.
- Ensure selected non-null patterns match at least one asset in the latest inspected release.
- Return valid JSON only for the object itself (no surrounding prose) unless the user asks for explanation.

Safety and idempotency rules:

- Always check whether an entry with the same `appName` or `repoURL` already exists.
- If present, update in place instead of duplicating.
- If duplicate entries already exist, keep one and remove extras.
- Always perform dry-run before writing.
- Keep a backup when writing.
- Never mutate unrelated installer entries.

Helper scripts available in this skill:

- `.github/skills/make-github-installer-config/scripts/scan_github_releases.py`
- `.github/skills/make-github-installer-config/scripts/build_installer_config.py`
- `.github/skills/make-github-installer-config/scripts/upsert_installer_data.py`
