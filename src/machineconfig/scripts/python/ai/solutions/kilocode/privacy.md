# Privacy defaults for Kilo Code

- Keep API keys and tokens in environment variables, never in tracked files.
- Treat exported `kilo-code-settings.json` as sensitive because it can contain API keys in plaintext.
- Keep `.kilocodeignore` up to date so secrets (`.env`, `secrets/`, key files) are not readable by tools.
- Use `.kilocode/mcp.json` for shared MCP servers and pass credentials through environment variables.
- Keep MCP auto-approval disabled unless you explicitly trust each MCP tool.
