# cloud

Cloud provider management and data synchronization.

---

## Usage

```bash
cloud [OPTIONS] COMMAND [ARGS]...
```

---

## Configuration

### config

Configure cloud storage providers.

```bash
cloud config [PROVIDER]
```

**Supported Providers:**

- `onedrive` - Microsoft OneDrive
- `gdrive` - Google Drive
- `dropbox` - Dropbox
- `s3` - Amazon S3
- `azure` - Azure Blob Storage
- `sftp` - SFTP server

---

### setup-encrypted

Create an encrypted remote for sensitive data.

```bash
cloud setup-encrypted NAME [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--backend` | Backend remote to encrypt |
| `--password` | Encryption password |

---

## Sync Operations

### sync

Synchronize files between locations.

```bash
cloud sync SOURCE DESTINATION [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview without changes |
| `--mirror` | Make destination identical |
| `--bidirectional` | Two-way sync |
| `--delete` | Delete extra files in destination |

**Examples:**

```bash
# Sync to cloud
cloud sync ~/documents gdrive:documents

# Mirror a directory
cloud sync --mirror ~/data backup:data

# Preview sync
cloud sync --dry-run ~/important remote:backup
```

---

### backup

Create a backup of local data.

```bash
cloud backup PATH [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--destination` | Backup destination |
| `--compress` | Compress backup |
| `--encrypt` | Encrypt backup |

---

### restore

Restore data from backup.

```bash
cloud restore SOURCE DESTINATION [OPTIONS]
```

---

## Management

### list

List files in remote storage.

```bash
cloud list REMOTE:PATH
```

---

### list-backups

List available backups.

```bash
cloud list-backups [REMOTE]
```

---

### info

Show information about remote storage.

```bash
cloud info [REMOTE]
```

---

## Scheduling

### schedule-backup

Set up automatic backups.

```bash
cloud schedule-backup PATH [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--interval` | hourly, daily, weekly |
| `--destination` | Backup destination |

---

## Examples

```bash
# Configure OneDrive
cloud config onedrive

# Sync documents
cloud sync ~/documents onedrive:documents

# Create encrypted backup
cloud backup ~/secrets --encrypt --destination encrypted:backup

# Restore from backup
cloud restore onedrive:backup/2024-01-15 ~/restored

# Schedule daily backup
cloud schedule-backup ~/important --interval daily
```
