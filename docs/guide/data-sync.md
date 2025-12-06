# Data Sync

Backup and synchronize your data across machines and cloud storage.

---

## Overview

Machineconfig integrates with [rclone](https://rclone.org/) to provide powerful data synchronization capabilities:

- Sync to cloud storage providers
- Encrypted backups
- Incremental syncing
- Cross-platform support

---

## Supported Backends

| Provider | Status |
|----------|--------|
| OneDrive | Full support |
| Google Drive | Full support |
| Dropbox | Full support |
| AWS S3 | Full support |
| Azure Blob | Full support |
| SFTP | Full support |
| Local | Full support |

---

## Quick Start

### Configure Cloud Provider

```bash
cloud config
```

This walks you through setting up your preferred cloud provider.

### Sync Data

```bash
cloud sync /local/path remote:path
```

### Backup

```bash
cloud backup /important/data
```

---

## Sync Strategies

### Mirror

One-way sync that makes destination identical to source:

```bash
cloud sync --mirror source/ dest/
```

### Bidirectional

Two-way sync that merges changes:

```bash
cloud sync --bidirectional source/ dest/
```

---

## Encryption

Encrypt sensitive data before uploading:

```bash
# Setup encrypted remote
cloud setup-encrypted myencrypted

# Sync to encrypted remote
cloud sync ~/secrets myencrypted:secrets
```

---

## Scheduled Backups

Set up automatic backups:

```bash
cloud schedule-backup ~/documents --interval daily
```

---

## Data Recovery

Restore from backup:

```bash
cloud restore backup:documents ~/documents
```

List available backups:

```bash
cloud list-backups
```

---

## Best Practices

1. **Use encryption** for sensitive data
2. **Test restores** regularly
3. **Use multiple backends** for critical data
4. **Monitor sync status** for issues
