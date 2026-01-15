#!/usr/bin/env python3
"""HTML scraper for GitHub release pages as fallback when API rate limit is exceeded."""

import re
from typing import Any, Optional
import requests


def extract_tag_from_html(html: str, owner: str, repo: str) -> str:
    patterns = [
        rf'/{re.escape(owner)}/{re.escape(repo)}/releases/tag/([^"\'<>\s]+)',
        rf'/{re.escape(owner)}/{re.escape(repo)}/tree/([^"\'<>\s]+)',
        r'<span[^>]*class="[^"]*ml-1[^"]*"[^>]*>([^<]+)</span>',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            tag = match.group(1).strip()
            if tag and not tag.startswith("http"):
                return tag
    return ""


def extract_release_name(html: str) -> str:
    patterns = [
        r'<h1[^>]*class="[^"]*d-inline[^"]*"[^>]*>([^<]+)</h1>',
        r'<bdi[^>]*class="[^"]*mr-2[^"]*"[^>]*>([^<]+)</bdi>',
        r'<h1[^>]*>([^<]+)</h1>',
    ]
    for pattern in patterns:
        match = re.search(pattern, html)
        if match:
            name = match.group(1).strip()
            if name:
                return name
    return ""


def extract_published_at(html: str) -> str:
    pattern = r'<relative-time[^>]*datetime="([^"]+)"'
    match = re.search(pattern, html)
    if match:
        return match.group(1)
    return ""


def fetch_expanded_assets(username: str, repo_name: str, tag_name: str, headers: dict[str, str]) -> list[dict[str, Any]]:
    """Fetch assets from the expanded_assets endpoint which contains all downloadable files."""
    assets: list[dict[str, Any]] = []
    expanded_url = f"https://github.com/{username}/{repo_name}/releases/expanded_assets/{tag_name}"
    try:
        response = requests.get(expanded_url, timeout=30, headers=headers)
        if response.status_code != 200:
            print(f"⚠️ [Scraper] Could not fetch expanded assets for {username}/{repo_name}: HTTP {response.status_code}")
            return assets
        html = response.text
        pattern = r'href="([^"]*?/releases/download/[^"]+)"[^>]*>.*?<span[^>]*class="[^"]*Truncate-text[^"]*text-bold[^"]*"[^>]*>([^<]+)</span>'
        seen_urls: set[str] = set()
        matches = re.findall(pattern, html, re.DOTALL)
        for href, name in matches:
            asset_name = name.strip()
            if not asset_name or asset_name.isspace():
                continue
            download_url = f"https://github.com{href}" if href.startswith("/") else href
            if download_url in seen_urls:
                continue
            seen_urls.add(download_url)
            assets.append({"name": asset_name, "size": 0, "download_count": 0, "content_type": "", "created_at": "", "updated_at": "", "browser_download_url": download_url})
    except requests.RequestException as error:
        print(f"⚠️ [Scraper] Error fetching expanded assets for {username}/{repo_name}: {error}")
    return assets


def scrape_github_release_page(username: str, repo_name: str, version: Optional[str] = None) -> Optional[dict[str, Any]]:
    """Scrape GitHub release page HTML to extract release information. Falls back to this when API rate limit is hit."""
    try:
        requested_version = (version or "").strip()
        if requested_version and requested_version.lower() != "latest":
            url = f"https://github.com/{username}/{repo_name}/releases/tag/{requested_version}"
        else:
            url = f"https://github.com/{username}/{repo_name}/releases/latest"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
        response = requests.get(url, timeout=30, headers=headers, allow_redirects=True)
        if response.status_code != 200:
            print(f"❌ [Scraper] Failed to fetch page for {username}/{repo_name}: HTTP {response.status_code}")
            return None
        html = response.text
        tag_name = extract_tag_from_html(html, username, repo_name)
        if not tag_name:
            print(f"🔍 [Scraper] No tag found for {username}/{repo_name}")
            return None
        release_name = extract_release_name(html) or tag_name
        published_at = extract_published_at(html)
        assets = fetch_expanded_assets(username, repo_name, tag_name, headers)
        print(f"✅ [Scraper] Found {len(assets)} assets for {username}/{repo_name} @ {tag_name}")
        return {"tag_name": tag_name, "name": release_name, "published_at": published_at, "assets": assets}
    except requests.RequestException as error:
        print(f"❌ [Scraper] Error fetching {username}/{repo_name}: {error}")
        return None
