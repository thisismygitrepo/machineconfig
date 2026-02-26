---
applyTo: "**"
---

# Copilot CLI security and privacy guardrails

* Run Copilot CLI only from trusted project directories. Avoid launching from `$HOME` or other sensitive folders.
* Keep personal configuration under `~/.copilot` (or custom `XDG_CONFIG_HOME`) and never commit secrets.
* Prefer scoped permissions (`--allow-tool`, `--deny-tool`, `--allow-url`, `--deny-url`) instead of broad `--allow-all`/`--yolo`.
* For PAT-based MCP authentication, use environment variables (for example `GITHUB_PERSONAL_ACCESS_TOKEN`) instead of hardcoded tokens.
* Review and maintain `trusted_folders`, `allowed_urls`, and `denied_urls` in `~/.copilot/config.json`.

# Copilot CLI MCP and config notes

* Copilot CLI includes the GitHub MCP server by default (`github-mcp-server`) with read-only tools enabled.
* Configure additional MCP servers with `/mcp add`, then inspect with `/mcp show`.
* MCP server definitions are stored in `~/.copilot/mcp-config.json`.
* Use `--add-github-mcp-toolset`, `--add-github-mcp-tool`, `--enable-all-github-mcp-tools`, or `--disable-builtin-mcps` when you need to adjust MCP exposure per run.
