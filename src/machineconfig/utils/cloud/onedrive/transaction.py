"""
OneDrive transaction functions for uploading and downloading files.

This module provides standalone functions to interact with Microsoft OneDrive
using the Microsoft Graph API. It supports both rclone tokens and direct OAuth2 authentication.

Key Features:
- Automatic token refresh when expired
- Persistent token storage
- Direct OAuth2 setup without rclone dependency
- Upload/download files with progress tracking
- Support for both small and large file uploads

Requirements:
    pip install requests

Setup Options:

    Option 1: Direct OAuth2 Setup (Recommended)
    1. Run setup_oauth_authentication() for first-time setup
    2. Follow the interactive prompts to authorize
    3. Tokens will be automatically saved and refreshed

    Option 2: Using existing rclone token
    1. Update the RCLONE_TOKEN with your rclone token
    2. Set DRIVE_ID from your rclone config
    3. The system will automatically attempt to refresh when expired

Environment Variables (for OAuth2):
    ONEDRIVE_CLIENT_ID: Your Azure App Registration Client ID
    ONEDRIVE_CLIENT_SECRET: Your Client Secret (optional for public clients)
    ONEDRIVE_REDIRECT_URI: Redirect URI (default: http://localhost:8080/callback)
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Any
import requests
from urllib.parse import quote
import json


def get_rclone_token(section: str):
    import platform

    if platform.system() == "Windows":
        rclone_file_path = Path(os.getenv("APPDATA", "")) / "rclone" / "rclone.conf"
    else:
        rclone_file_path = Path.home() / ".config" / "rclone" / "rclone.conf"
    if rclone_file_path.exists():
        import configparser

        config = configparser.ConfigParser()
        config.read(rclone_file_path)
        if section in config:
            results = config[section]
            # something like {"token": {"access_token": "...", "expiry": "..."}, "drive_id": "...", "drive_type": "..."}
            return dict(results)
    return None


# Configuration - Will be loaded from rclone config
_cached_config = None


def get_config(section: str = "odp") -> dict[str, Any]:
    """
    Get OneDrive configuration from rclone config.

    Args:
        section: The rclone config section name (default: "odp")

    Returns:
        Dictionary containing token, drive_id, and drive_type
    """
    global _cached_config
    if _cached_config is None:
        rclone_config = get_rclone_token(section)
        if not rclone_config:
            raise Exception(f"Could not find rclone config section '{section}'. Please set up rclone first.")

        # Parse the token from rclone config
        token_str = rclone_config.get("token", "{}")
        try:
            token_data = json.loads(token_str)
        except json.JSONDecodeError:
            raise Exception(f"Invalid token format in rclone config section '{section}'")

        _cached_config = {"token": token_data, "drive_id": rclone_config.get("drive_id"), "drive_type": rclone_config.get("drive_type", "personal")}

    return _cached_config


def get_token() -> dict[str, Any]:
    """Get the current token from rclone config."""
    return get_config()["token"]


def get_drive_id():
    """Get the drive ID from rclone config."""
    return get_config()["drive_id"]


def get_drive_type():
    """Get the drive type from rclone config."""
    return get_config()["drive_type"]


def clear_config_cache():
    """Clear the cached config to force reload from rclone."""
    global _cached_config
    _cached_config = None


# OAuth2 Configuration - You'll need to set these up in Azure App Registration
CLIENT_ID = os.getenv("ONEDRIVE_CLIENT_ID", "your_client_id_here")
CLIENT_SECRET = os.getenv("ONEDRIVE_CLIENT_SECRET", "your_client_secret_here")  # Optional for public clients
REDIRECT_URI = os.getenv("ONEDRIVE_REDIRECT_URI", "http://localhost:8080/callback")

# Microsoft Graph API endpoints
GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"
OAUTH_TOKEN_ENDPOINT = "https://login.microsoftonline.com/common/oauth2/v2.0/token"


def is_token_valid() -> bool:
    """
    Check if the current rclone token is still valid.

    Returns:
        True if token is valid, False otherwise
    """
    try:
        token = get_token()
        # Parse the expiry time from rclone format
        expiry_str = token.get("expiry")
        if not expiry_str:
            return False

        # Remove timezone info for parsing (rclone format includes timezone)
        if "+" in expiry_str:
            expiry_str = expiry_str.split("+")[0]
        elif "Z" in expiry_str:
            expiry_str = expiry_str.replace("Z", "")

        expiry_time = datetime.fromisoformat(expiry_str)
        current_time = datetime.now()

        # Add some buffer time (5 minutes)
        return expiry_time > current_time + timedelta(minutes=5)
    except Exception as e:
        print(f"Error checking token validity: {e}")
        return False


def get_access_token() -> Optional[str]:
    """
    Get access token, automatically refreshing if expired.

    Returns:
        Access token string or None if token cannot be obtained/refreshed
    """
    # First try to load token from file if it exists
    load_token_from_file()

    if not is_token_valid():
        print("🔄 Access token has expired, attempting to refresh...")

        # Try to refresh the token
        refreshed_token = refresh_access_token()
        if refreshed_token:
            return refreshed_token["access_token"]
        else:
            print("❌ Failed to refresh token automatically!")
            print("\n🔧 You have two options:")
            print("1. Run setup_oauth_authentication() to set up OAuth")
            print("2. Update your rclone token by running: rclone config reconnect odp")
            return None

    token = get_token()
    return token.get("access_token")


def make_graph_request(method: str, endpoint: str, **kwargs: Any) -> requests.Response:
    """
    Make authenticated request to Microsoft Graph API.

    Args:
        method: HTTP method (GET, POST, PUT, etc.)
        endpoint: API endpoint (without base URL)
        **kwargs: Additional arguments for requests

    Returns:
        Response object

    Raises:
        Exception: If authentication fails or request fails
    """
    token = get_access_token()
    if not token:
        raise Exception("Failed to get valid access token")

    headers = kwargs.get("headers", {})
    headers["Authorization"] = f"Bearer {token}"
    kwargs["headers"] = headers

    url = f"{GRAPH_API_BASE}/{endpoint.lstrip('/')}"
    response = requests.request(method, url, **kwargs)

    return response


def push_to_onedrive(local_path: str, remote_path: str) -> bool:
    """
    Push a file from local system to OneDrive.

    Args:
        local_path: Path to the local file
        remote_path: Path where the file should be stored in OneDrive
                    (e.g., "/Documents/myfile.txt")

    Returns:
        True if successful, False otherwise
    """
    local_file = Path(local_path)

    if not local_file.exists():
        print(f"Local file does not exist: {local_path}")
        return False

    if not local_file.is_file():
        print(f"Path is not a file: {local_path}")
        return False

    # Ensure remote path starts with /
    if not remote_path.startswith("/"):
        remote_path = "/" + remote_path

    # Create parent directories if they don't exist
    remote_dir = os.path.dirname(remote_path)
    if remote_dir and remote_dir != "/":
        create_remote_directory(remote_dir)

    try:
        file_size = local_file.stat().st_size

        # For small files (< 4MB), use simple upload
        if file_size < 4 * 1024 * 1024:
            return simple_upload(local_file, remote_path)
        else:
            return resumable_upload(local_file, remote_path)

    except Exception as e:
        print(f"Error uploading file: {e}")
        return False


def simple_upload(local_file: Path, remote_path: str) -> bool:
    """Upload small files using simple upload."""
    try:
        with open(local_file, "rb") as f:
            file_content = f.read()

        # URL encode the remote path and use specific drive
        encoded_path = quote(remote_path, safe="/")
        drive_id = get_drive_id()
        endpoint = f"drives/{drive_id}/root:{encoded_path}:/content"

        response = make_graph_request("PUT", endpoint, data=file_content)

        if response.status_code in [200, 201]:
            print(f"Successfully uploaded: {local_file} -> {remote_path}")
            return True
        else:
            print(f"Upload failed: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"Simple upload error: {e}")
        return False


def resumable_upload(local_file: Path, remote_path: str) -> bool:
    """Upload large files using resumable upload."""
    try:
        # Create upload session using specific drive
        encoded_path = quote(remote_path, safe="/")
        drive_id = get_drive_id()
        endpoint = f"drives/{drive_id}/root:{encoded_path}:/createUploadSession"

        item_data = {"item": {"@microsoft.graph.conflictBehavior": "replace", "name": local_file.name}}

        response = make_graph_request("POST", endpoint, json=item_data)

        if response.status_code != 200:
            print(f"Failed to create upload session: {response.status_code} - {response.text}")
            return False

        upload_url = response.json()["uploadUrl"]
        file_size = local_file.stat().st_size
        chunk_size = 320 * 1024  # 320KB chunks

        with open(local_file, "rb") as f:
            bytes_uploaded = 0

            while bytes_uploaded < file_size:
                chunk_data = f.read(chunk_size)
                if not chunk_data:
                    break

                chunk_end = min(bytes_uploaded + len(chunk_data) - 1, file_size - 1)

                headers = {"Content-Range": f"bytes {bytes_uploaded}-{chunk_end}/{file_size}", "Content-Length": str(len(chunk_data))}

                chunk_response = requests.put(upload_url, data=chunk_data, headers=headers)

                if chunk_response.status_code in [202, 200, 201]:
                    bytes_uploaded += len(chunk_data)
                    progress = (bytes_uploaded / file_size) * 100
                    print(f"Upload progress: {progress:.1f}%")
                else:
                    print(f"Chunk upload failed: {chunk_response.status_code} - {chunk_response.text}")
                    return False

        print(f"Successfully uploaded: {local_file} -> {remote_path}")
        return True

    except Exception as e:
        print(f"Resumable upload error: {e}")
        return False


def pull_from_onedrive(remote_path: str, local_path: str) -> bool:
    """
    Pull a file from OneDrive to local system.

    Args:
        remote_path: Path to the file in OneDrive (e.g., "/Documents/myfile.txt")
        local_path: Path where the file should be saved locally

    Returns:
        True if successful, False otherwise
    """
    # Ensure remote path starts with /
    if not remote_path.startswith("/"):
        remote_path = "/" + remote_path

    try:
        # Get file metadata and download URL using specific drive
        encoded_path = quote(remote_path, safe="/")
        drive_id = get_drive_id()
        endpoint = f"drives/{drive_id}/root:{encoded_path}"

        response = make_graph_request("GET", endpoint)

        if response.status_code == 404:
            print(f"File not found in OneDrive: {remote_path}")
            return False
        elif response.status_code != 200:
            print(f"Failed to get file info: {response.status_code} - {response.text}")
            return False

        file_info = response.json()

        # Check if it's a file (not a folder)
        if "folder" in file_info:
            print(f"Path is a folder, not a file: {remote_path}")
            return False

        # Get download URL
        download_url = file_info.get("@microsoft.graph.downloadUrl")
        if not download_url:
            print("No download URL available")
            return False

        # Create local directory if it doesn't exist
        local_file = Path(local_path)
        local_file.parent.mkdir(parents=True, exist_ok=True)

        # Download the file
        download_response = requests.get(download_url, stream=True)
        download_response.raise_for_status()

        file_size = int(file_info.get("size", 0))
        bytes_downloaded = 0

        with open(local_file, "wb") as f:
            for chunk in download_response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    bytes_downloaded += len(chunk)

                    if file_size > 0:
                        progress = (bytes_downloaded / file_size) * 100
                        print(f"Download progress: {progress:.1f}%")

        print(f"Successfully downloaded: {remote_path} -> {local_path}")
        return True

    except Exception as e:
        print(f"Error downloading file: {e}")
        return False


def create_remote_directory(remote_path: str) -> bool:
    """
    Create a directory in OneDrive if it doesn't exist.

    Args:
        remote_path: Path to the directory in OneDrive

    Returns:
        True if successful or already exists, False otherwise
    """
    if not remote_path or remote_path == "/":
        return True

    # Ensure remote path starts with /
    if not remote_path.startswith("/"):
        remote_path = "/" + remote_path

    try:
        # Check if directory already exists using specific drive
        encoded_path = quote(remote_path, safe="/")
        drive_id = get_drive_id()
        endpoint = f"drives/{drive_id}/root:{encoded_path}"

        response = make_graph_request("GET", endpoint)

        if response.status_code == 200:
            # Directory already exists
            return True
        elif response.status_code != 404:
            print(f"Error checking directory: {response.status_code} - {response.text}")
            return False

        # Create parent directory first
        parent_dir = os.path.dirname(remote_path)
        if parent_dir and parent_dir != "/":
            if not create_remote_directory(parent_dir):
                return False

        # Create the directory
        dir_name = os.path.basename(remote_path)
        parent_encoded = quote(parent_dir if parent_dir else "/", safe="/")

        if parent_dir and parent_dir != "/":
            endpoint = f"drives/{drive_id}/root:{parent_encoded}:/children"
        else:
            endpoint = f"drives/{drive_id}/root/children"

        folder_data = {"name": dir_name, "folder": {}, "@microsoft.graph.conflictBehavior": "replace"}

        response = make_graph_request("POST", endpoint, json=folder_data)

        if response.status_code in [200, 201]:
            return True
        else:
            print(f"Failed to create directory: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"Error creating directory: {e}")
        return False


def refresh_access_token() -> Optional[dict[str, Any]]:
    """
    Refresh the access token using the refresh token.

    Returns:
        New token dictionary with access_token, refresh_token, and expiry, or None if failed
    """
    token = get_token()
    refresh_token = token.get("refresh_token")
    if not refresh_token:
        print("ERROR: No refresh token available!")
        return None

    print("🔄 Refreshing access token...")

    # Prepare the token refresh request
    data = {"client_id": CLIENT_ID, "grant_type": "refresh_token", "refresh_token": refresh_token, "scope": "https://graph.microsoft.com/Files.ReadWrite.All offline_access"}

    # Add client secret if available (for confidential clients)
    if CLIENT_SECRET and CLIENT_SECRET != "your_client_secret_here":
        data["client_secret"] = CLIENT_SECRET

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post(OAUTH_TOKEN_ENDPOINT, data=data, headers=headers)

        if response.status_code == 200:
            token_data = response.json()

            # Calculate expiry time (tokens typically last 1 hour)
            expires_in = token_data.get("expires_in", 3600)  # Default to 1 hour
            expiry_time = datetime.now() + timedelta(seconds=expires_in)

            # Update the cached token configuration
            new_token = {
                "access_token": token_data["access_token"],
                "token_type": token_data.get("token_type", "Bearer"),
                "refresh_token": token_data.get("refresh_token", refresh_token),  # Use new or keep old
                "expiry": expiry_time.isoformat(),
            }

            # Update the cached config
            global _cached_config
            if _cached_config is not None:
                _cached_config["token"] = new_token
            else:
                clear_config_cache()  # Force reload on next access

            print("✅ Access token refreshed successfully!")
            print(f"🕒 New token expires at: {expiry_time}")

            # Optionally save the new token to a file for persistence
            save_token_to_file(new_token)

            return new_token

        else:
            print(f"❌ Token refresh failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error refreshing token: {e}")
        return None


def save_token_to_file(token_data: dict[str, Any], file_path: Optional[str] = None) -> bool:
    """
    Save token data to a file for persistence.

    Args:
        token_data: Token dictionary to save
        file_path: Optional path to save the token file

    Returns:
        True if successful, False otherwise
    """
    if not file_path:
        # Default to a hidden file in user's home directory
        file_path = os.path.expanduser("~/.onedrive_token.json")

    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as f:
            json.dump(token_data, f, indent=2)

        # Set restrictive permissions (readable only by owner)
        os.chmod(file_path, 0o600)

        print(f"💾 Token saved to: {file_path}")
        return True

    except Exception as e:
        print(f"❌ Error saving token: {e}")
        return False


def load_token_from_file(file_path: Optional[str] = None) -> Optional[dict[str, Any]]:
    """
    Load token data from a file.

    Args:
        file_path: Optional path to load the token file from

    Returns:
        Token dictionary or None if failed
    """
    if not file_path:
        file_path = os.path.expanduser("~/.onedrive_token.json")

    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                token_data = json.load(f)

            # Update the cached config token
            global _cached_config
            if _cached_config is not None:
                _cached_config["token"] = token_data
            else:
                clear_config_cache()  # Force reload on next access

            print(f"📂 Token loaded from: {file_path}")
            return token_data
        else:
            print(f"ℹ️  No saved token file found at: {file_path}")
            return None

    except Exception as e:
        print(f"❌ Error loading token: {e}")
        return None


def get_authorization_url() -> str:
    """
    Generate the authorization URL for initial OAuth setup.
    This is needed only for the first-time setup to get the initial tokens.

    Returns:
        Authorization URL string
    """
    from urllib.parse import urlencode

    params = {"client_id": CLIENT_ID, "response_type": "code", "redirect_uri": REDIRECT_URI, "response_mode": "query", "scope": "https://graph.microsoft.com/Files.ReadWrite.All offline_access", "state": "onedrive_auth"}

    auth_url = f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?{urlencode(params)}"
    return auth_url


def exchange_authorization_code(authorization_code: str) -> Optional[dict[str, Any]]:
    """
    Exchange authorization code for initial tokens.
    This is used during the first-time OAuth setup.

    Args:
        authorization_code: The authorization code received from the callback

    Returns:
        Token dictionary or None if failed
    """
    data = {"client_id": CLIENT_ID, "grant_type": "authorization_code", "code": authorization_code, "redirect_uri": REDIRECT_URI, "scope": "https://graph.microsoft.com/Files.ReadWrite.All offline_access"}

    # Add client secret if available
    if CLIENT_SECRET and CLIENT_SECRET != "your_client_secret_here":
        data["client_secret"] = CLIENT_SECRET

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post(OAUTH_TOKEN_ENDPOINT, data=data, headers=headers)

        if response.status_code == 200:
            token_data = response.json()

            # Calculate expiry time
            expires_in = token_data.get("expires_in", 3600)
            expiry_time = datetime.now() + timedelta(seconds=expires_in)

            new_token = {"access_token": token_data["access_token"], "token_type": token_data.get("token_type", "Bearer"), "refresh_token": token_data["refresh_token"], "expiry": expiry_time.isoformat()}

            # Update cached config and save
            global _cached_config
            if _cached_config is not None:
                _cached_config["token"] = new_token
            else:
                clear_config_cache()  # Force reload on next access
            save_token_to_file(new_token)

            print("✅ Initial tokens obtained successfully!")
            return new_token

        else:
            print(f"❌ Token exchange failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error exchanging authorization code: {e}")
        return None


def setup_oauth_authentication():
    """
    Interactive setup for OAuth authentication.
    Run this once to set up initial authentication.
    """
    print("🔧 Setting up OneDrive OAuth Authentication")
    print("=" * 50)

    if CLIENT_ID == "your_client_id_here":
        print("❌ You need to set up Azure App Registration first!")
        print("\n📋 Setup Instructions:")
        print("1. Go to https://portal.azure.com")
        print("2. Navigate to 'Azure Active Directory' > 'App registrations'")
        print("3. Click 'New registration'")
        print("4. Set Name: 'OneDrive API Access'")
        print("5. Set Redirect URI: http://localhost:8080/callback")
        print("6. After creation, copy the 'Application (client) ID'")
        print("7. Go to 'API permissions' > 'Add permission' > 'Microsoft Graph'")
        print("8. Add 'Files.ReadWrite.All' and 'offline_access' permissions")
        print("9. Set environment variables:")
        print("   export ONEDRIVE_CLIENT_ID='your_client_id'")
        print("   export ONEDRIVE_REDIRECT_URI='http://localhost:8080/callback'")
        return

    print(f"Using Client ID: {CLIENT_ID}")
    print(f"Redirect URI: {REDIRECT_URI}")

    # Generate authorization URL
    auth_url = get_authorization_url()
    print("\n🌐 Please visit this URL to authorize the application:")
    print(f"{auth_url}")

    print("\n📋 After authorization, you'll be redirected to:")
    print(f"{REDIRECT_URI}?code=AUTHORIZATION_CODE&state=onedrive_auth")
    print("\n🔑 Copy the 'code' parameter from the URL and paste it below:")

    auth_code = input("Authorization Code: ").strip()

    if auth_code:
        token_data = exchange_authorization_code(auth_code)
        if token_data:
            print("\n✅ OAuth setup completed successfully!")
            print("🎉 You can now use the OneDrive functions without rclone!")
        else:
            print("\n❌ OAuth setup failed. Please try again.")
    else:
        print("\n❌ No authorization code provided.")


# Example usage
if __name__ == "__main__":
    # Try to load existing token from file
    load_token_from_file()

    print("OneDrive transaction functions loaded.")
    try:
        config = get_config()
        print(f"Drive ID: {get_drive_id()}")
        print(f"Drive Type: {get_drive_type()}")

        if is_token_valid():
            print("✅ Token is valid and ready to use")
        else:
            print("⚠️  Token has expired or is invalid")

            # Try to refresh automatically
            if refresh_access_token():
                print("✅ Token refreshed successfully")
            else:
                print("❌ Failed to refresh token automatically")
                print("\n🔧 Setup Instructions:")
                print("1. First-time setup: run setup_oauth_authentication()")
                print("2. Or update rclone token: rclone config reconnect odp")
    except Exception as e:
        print(f"❌ Error loading rclone config: {e}")
        print("Please ensure rclone is configured with an 'odp' section")

    print("\n📚 Available Functions:")
    print("• push_to_onedrive(local_path, remote_path)")
    print("• pull_from_onedrive(remote_path, local_path)")
    print("• refresh_access_token() - Refresh expired tokens")
    print("• setup_oauth_authentication() - First-time OAuth setup")
    print("• save_token_to_file(token_data) - Save tokens for persistence")
    print("• load_token_from_file() - Load saved tokens")

    print("\n💡 Example usage:")
    print("push_to_onedrive('/home/user/document.pdf', '/Documents/document.pdf')")
    print("pull_from_onedrive('/Documents/document.pdf', '/home/user/downloaded.pdf')")

    # Uncomment to test with a file
    # push_to_onedrive('/home/alex/Downloads/users.xlsx', '/Documents/users.xlsx')
