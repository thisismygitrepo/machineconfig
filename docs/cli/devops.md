# devops

DevOps operations, package management, and system administration.

---

## Usage

```bash
devops [OPTIONS] COMMAND [ARGS]...
```

---

## Package Management

### install

Install one or more packages.

```bash
devops install PACKAGES...
```

**Example:**

```bash
devops install ripgrep fd bat
```

---

### install-essentials

Install a curated set of modern CLI tools.

```bash
devops install-essentials [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--minimal` | Install only core tools |
| `--full` | Install all recommended tools |

---

### install-group

Install a predefined group of packages.

```bash
devops install-group GROUP
```

**Available Groups:**

| Group | Contents |
|-------|----------|
| `dev` | Development tools |
| `sysadmin` | System administration |
| `datascience` | Data science tools |

---

### check-installations

Check which tools are installed and their versions.

```bash
devops check-installations [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--json` | Output as JSON |
| `--missing` | Show only missing tools |

---

## System Operations

### update-system

Update system packages and installed tools.

```bash
devops update-system [OPTIONS]
```

---

### service

Manage system services.

```bash
devops service [ACTION] SERVICE
```

**Actions:**

| Action | Description |
|--------|-------------|
| `start` | Start service |
| `stop` | Stop service |
| `restart` | Restart service |
| `status` | Show service status |
| `logs` | Show service logs |

---

### health-check

Run system health checks.

```bash
devops health-check [OPTIONS]
```

---

## Scheduling

### schedule

Schedule a command to run periodically.

```bash
devops schedule "COMMAND" --cron "CRON_EXPRESSION"
```

**Example:**

```bash
devops schedule "cloud backup ~/data" --cron "0 2 * * *"
```

---

### schedule-list

List scheduled tasks.

```bash
devops schedule-list
```

---

### schedule-remove

Remove a scheduled task.

```bash
devops schedule-remove TASK_ID
```

---

## Examples

```bash
# Install essential tools
devops install-essentials

# Check what's installed
devops check-installations

# Update everything
devops update-system

# Manage services
devops service status nginx

# Schedule daily backup
devops schedule "cloud sync ~/data remote:backup" --cron "0 3 * * *"
```
