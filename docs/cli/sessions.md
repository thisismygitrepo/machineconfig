# sessions

Terminal session management for persistent and remote sessions.

---

## Usage

```bash
sessions [OPTIONS] COMMAND [ARGS]...
```

---

## Session Management

### list

List all active sessions.

```bash
sessions list [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--all` | Include inactive sessions |
| `--json` | Output as JSON |

---

### create

Create a new session.

```bash
sessions create NAME [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--shell` | Shell to use |
| `--directory` | Starting directory |

---

### attach

Attach to an existing session.

```bash
sessions attach NAME
```

---

### detach

Detach from current session.

```bash
sessions detach
```

---

### kill

Terminate a session.

```bash
sessions kill NAME
```

---

## Remote Execution

### exec

Execute a command on remote targets.

```bash
sessions exec "COMMAND" [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--targets` | Comma-separated list of hosts |
| `--parallel` | Execute in parallel |
| `--timeout` | Command timeout |

**Example:**

```bash
sessions exec "hostname && uptime" --targets server1,server2,server3
```

---

### connect

Connect to a remote machine.

```bash
sessions connect HOST [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--user` | SSH username |
| `--key` | SSH key file |
| `--port` | SSH port |

---

## Session Types

Machineconfig supports multiple session backends:

| Backend | Description |
|---------|-------------|
| `tmux` | Terminal multiplexer |
| `screen` | GNU Screen |
| `zellij` | Modern terminal workspace |

### Using a Specific Backend

```bash
sessions --backend tmux create dev
sessions --backend zellij create dev
```

---

## Examples

```bash
# List all sessions
sessions list

# Create a development session
sessions create dev --directory ~/projects

# Attach to session
sessions attach dev

# Execute on multiple servers
sessions exec "apt update" --targets web1,web2,db1

# Connect to remote
sessions connect myserver --user admin
```
