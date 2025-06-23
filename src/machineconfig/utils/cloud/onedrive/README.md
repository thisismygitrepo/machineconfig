# OneDrive API without rclone

This module provides direct OneDrive integration using Microsoft Graph API without requiring rclone.

## Features

- ✅ Automatic token refresh when expired
- ✅ Persistent token storage
- ✅ Upload/download files with progress tracking
- ✅ Support for large file uploads (chunked)
- ✅ Direct OAuth2 authentication setup

## Quick Start

### Option 1: Direct OAuth Setup (Recommended)

1. **Set up Azure App Registration:**
   - Go to [Azure Portal](https://portal.azure.com)
   - Navigate to 'Azure Active Directory' > 'App registrations'
   - Click 'New registration'
   - Name: 'OneDrive API Access'
   - Redirect URI: `http://localhost:8080/callback`
   - Add permissions: `Files.ReadWrite.All` and `offline_access`

2. **Set environment variables:**
   ```bash
   export ONEDRIVE_CLIENT_ID='your_client_id_here'
   export ONEDRIVE_REDIRECT_URI='http://localhost:8080/callback'
   ```

3. **Run initial setup:**
   ```python
   from transaction import setup_oauth_authentication
   setup_oauth_authentication()
   ```

### Option 2: Using existing rclone token

If you already have rclone configured, the system will automatically use and refresh your existing tokens.

## Usage Examples

```python
from transaction import push_to_onedrive, pull_from_onedrive

# Upload a file
success = push_to_onedrive('/path/to/local/file.pdf', '/Documents/file.pdf')

# Download a file
success = pull_from_onedrive('/Documents/file.pdf', '/path/to/local/downloaded.pdf')
```

## Token Management

### Automatic Token Refresh

The system automatically handles token refresh:

```python
from transaction import get_access_token

# This will automatically refresh if expired
token = get_access_token()
```

### Manual Token Operations

```python
from transaction import refresh_access_token, save_token_to_file, load_token_from_file

# Manually refresh token
new_token = refresh_access_token()

# Save token to file
save_token_to_file(token_data)

# Load token from file
token_data = load_token_from_file()
```

## How Token Renewal Works

1. **Automatic Detection**: The system checks token expiry before each API call
2. **Refresh Attempt**: If expired, it automatically uses the refresh token to get a new access token
3. **Persistent Storage**: New tokens are saved to `~/.onedrive_token.json` for future use
4. **Fallback**: If refresh fails, it provides clear instructions for manual intervention

## No rclone Required

This implementation eliminates the need for rclone by:

- Using Microsoft Graph API directly
- Implementing OAuth2 flow natively
- Managing token lifecycle automatically
- Providing persistent token storage

## Error Handling

The system gracefully handles various scenarios:

- Expired tokens → Automatic refresh
- Network errors → Detailed error messages
- Missing permissions → Clear setup instructions
- Invalid tokens → Step-by-step recovery guide

## Files Created

- `~/.onedrive_token.json`: Encrypted token storage (chmod 600)
- Token is automatically loaded on import

## Security

- Tokens are stored with restrictive permissions (600)
- Client secrets are optional (public client mode supported)
- Refresh tokens are securely managed
- No sensitive data in logs

## Troubleshooting

### Token Refresh Failed
```python
# Try manual refresh
from transaction import refresh_access_token
token = refresh_access_token()

# Or re-run OAuth setup
from transaction import setup_oauth_authentication
setup_oauth_authentication()
```

### Permission Errors
Make sure your Azure app has the correct permissions:
- `Files.ReadWrite.All` (Delegated)
- `offline_access` (Delegated)

### Network Issues
Check your firewall allows connections to:
- `https://login.microsoftonline.com`
- `https://graph.microsoft.com`
