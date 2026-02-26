## Gemini CLI configuration notes

- Project settings live at `.gemini/settings.json`; user settings live at `~/.gemini/settings.json`, and project settings override user settings.
- Project memory instructions are loaded from `GEMINI.md` (and `AGENTS.md` when configured in `context.fileName`).
- Keep secrets in environment variables (`$VAR` / `${VAR}`) and reference them from settings instead of hardcoding sensitive values.

## Privacy defaults

- Keep `privacy.usageStatisticsEnabled` disabled unless explicitly needed.
- Keep telemetry disabled by default (`telemetry.enabled: false`, `telemetry.logPrompts: false`, `telemetry.target: "local"`).
- Keep `security.environmentVariableRedaction.enabled` on to reduce accidental secret exposure to tools and MCP servers.

## MCP setup guide

- Configure MCP servers under `mcpServers` and use `mcp.allowed` / `mcp.excluded` to control which servers are active.
- Prefer explicit `includeTools` / `excludeTools` per server and keep `trust: false` unless you fully control the server.
- Example server entry:

```json
{
  "mcpServers": {
    "local_python_tools": {
      "command": "python",
      "args": [
        "-m",
        "my_mcp_server"
      ],
      "env": {
        "API_KEY": "$MY_MCP_API_KEY"
      },
      "timeout": 30000,
      "trust": false,
      "includeTools": [
        "safe_tool"
      ],
      "excludeTools": [
        "dangerous_tool"
      ]
    }
  }
}
```
