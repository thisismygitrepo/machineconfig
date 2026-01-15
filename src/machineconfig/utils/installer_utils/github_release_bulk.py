#!/usr/bin/env python3
"""
Script to fetch GitHub release information from installer JSON files.
Extracts GitHub repository URLs and fetches latest release data with rate limiting.
"""

import json
import requests
from pathlib import Path
from typing import Any, Dict, Optional, Set, TypedDict
from urllib.parse import urlparse

from machineconfig.utils.installer_utils.github_release_scraper import scrape_github_release_page


class AssetInfo(TypedDict):
    """Type definition for GitHub release asset information."""
    name: str
    size: int
    download_count: int
    content_type: str
    created_at: str
    updated_at: str
    browser_download_url: str


class ReleaseInfo(TypedDict):
    """Type definition for GitHub release information."""
    tag_name: str
    name: str
    published_at: str
    assets: list[AssetInfo]
    assets_count: int


class OutputData(TypedDict):
    """Type definition for the output JSON data structure."""
    generated_at: str
    total_repositories: int
    successful_fetches: int
    releases: Dict[str, Optional[ReleaseInfo]]


def is_github_repo(url: str) -> bool:
    """Check if URL is a GitHub repository URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc == "github.com" and len(parsed.path.split("/")) >= 3
    except Exception:
        return False
def extract_github_repos_from_json(json_file_path: Path) -> Set[str]:
    """Extract GitHub repository URLs from installer JSON file."""
    github_repos: Set[str] = set()
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        for installer in data.get("installers", []):
            repo_url = installer.get("repoURL", "")
            if is_github_repo(repo_url):
                github_repos.add(repo_url)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error reading {json_file_path}: {e}")
    return github_repos
def get_repo_name_from_url(repo_url: str) -> Optional[tuple[str, str]]:
    """Extract owner/repo from GitHub URL as a tuple (username, repo_name)."""
    try:
        parsed = urlparse(repo_url)
        path_parts = parsed.path.strip("/").split("/")
        return (path_parts[0], path_parts[1])
    except (IndexError, AttributeError):
        return None


def fetch_github_release_data(
    username: str,
    repo_name: str,
    version: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Fetch GitHub release data for the latest or a specific tag. Falls back to HTML scraping if API fails."""

    try:
        requested_version = (version or "").strip()
        if requested_version and requested_version.lower() != "latest":
            url = f"https://api.github.com/repos/{username}/{repo_name}/releases/tags/{requested_version}"
        else:
            url = f"https://api.github.com/repos/{username}/{repo_name}/releases/latest"

        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            print(f"⚠️ API failed for {username}/{repo_name}: HTTP {response.status_code}, trying HTML scraper...")
            return scrape_github_release_page(username, repo_name, version)

        response_data = response.json()
        message = response_data.get("message")
        if isinstance(message, str):
            if "API rate limit exceeded" in message:
                print(f"🚫 Rate limit exceeded for {username}/{repo_name}, trying HTML scraper...")
                return scrape_github_release_page(username, repo_name, version)
            if "Not Found" in message:
                print(f"🔍 No releases found via API for {username}/{repo_name}, trying HTML scraper...")
                return scrape_github_release_page(username, repo_name, version)

        return response_data

    except (requests.RequestException, requests.Timeout, json.JSONDecodeError) as error:
        print(f"⚠️ API error for {username}/{repo_name}: {error}, trying HTML scraper...")
        return scrape_github_release_page(username, repo_name, version)


def get_release_info(
    username: str,
    repo_name: str,
    version: Optional[str] = None,
) -> Optional[ReleaseInfo]:
    """Return sanitized release information for the requested repository."""
    release_data = fetch_github_release_data(username, repo_name, version)
    if not release_data:
        return None
    return extract_release_info(release_data)


def extract_release_info(release_data: Dict[str, Any]) -> Optional[ReleaseInfo]:
    """Extract relevant information from GitHub release data."""
    if not release_data:
        return None
    assets: list[AssetInfo] = []
    for asset in release_data.get("assets", []):
        asset_info: AssetInfo = {
            "name": asset.get("name", ""),
            "size": asset.get("size", 0),
            "download_count": asset.get("download_count", 0),
            "content_type": asset.get("content_type", ""),
            "created_at": asset.get("created_at", ""),
            "updated_at": asset.get("updated_at", ""),
            "browser_download_url": asset.get("browser_download_url", "")
        }
        assets.append(asset_info)
    return {
        "tag_name": release_data.get("tag_name", ""),
        "name": release_data.get("name", ""),
        "published_at": release_data.get("published_at", ""),
        "assets": assets,
        "assets_count": len(assets)
    }

