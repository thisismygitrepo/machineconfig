#!/usr/bin/env python3
"""HTML scraper for GitHub release pages as fallback when API rate limit is exceeded."""

import re
from typing import Any, Optional
from html.parser import HTMLParser
import requests


class GitHubReleasePageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tag_name: str = ""
        self.release_name: str = ""
        self.published_at: str = ""
        self.assets: list[dict[str, Any]] = []
        self._in_release_header: bool = False
        self._in_asset_link: bool = False
        self._current_asset_url: str = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_dict = {k: v for k, v in attrs if v is not None}
        if tag == "a":
            href = attr_dict.get("href", "")
            if "/releases/download/" in href:
                self._in_asset_link = True
                if href.startswith("/"):
                    self._current_asset_url = f"https://github.com{href}"
                else:
                    self._current_asset_url = href
        if tag == "relative-time":
            datetime_val = attr_dict.get("datetime", "")
            if datetime_val and not self.published_at:
                self.published_at = datetime_val

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._in_asset_link:
            self._in_asset_link = False
            self._current_asset_url = ""

    def handle_data(self, data: str) -> None:
        if self._in_asset_link and self._current_asset_url:
            asset_name = data.strip()
            if asset_name and not any(a["browser_download_url"] == self._current_asset_url for a in self.assets):
                self.assets.append({"name": asset_name, "size": 0, "download_count": 0, "content_type": "", "created_at": "", "updated_at": "", "browser_download_url": self._current_asset_url})


def extract_tag_from_url(html: str, owner: str, repo: str) -> str:
    pattern = rf'/{re.escape(owner)}/{re.escape(repo)}/releases/tag/([^"\'>\s]+)'
    match = re.search(pattern, html, re.IGNORECASE)
    if match:
        return match.group(1)
    pattern_expanded = rf'/{re.escape(owner)}/{re.escape(repo)}/tree/([^"\'>\s]+)'
    match = re.search(pattern_expanded, html, re.IGNORECASE)
    if match:
        return match.group(1)
    return ""


def extract_release_name(html: str) -> str:
    pattern = r'<h1[^>]*class="[^"]*d-inline[^"]*"[^>]*>([^<]+)</h1>'
    match = re.search(pattern, html)
    if match:
        return match.group(1).strip()
    pattern2 = r'<bdi[^>]*class="[^"]*mr-2[^"]*"[^>]*>([^<]+)</bdi>'
    match = re.search(pattern2, html)
    if match:
        return match.group(1).strip()
    return ""


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
        parser = GitHubReleasePageParser()
        parser.feed(html)
        tag_name = extract_tag_from_url(html, username, repo_name)
        release_name = extract_release_name(html) or tag_name
        if not tag_name and not parser.assets:
            print(f"🔍 [Scraper] No release data found for {username}/{repo_name}")
            return None
        return {"tag_name": tag_name, "name": release_name, "published_at": parser.published_at, "assets": parser.assets}
    except requests.RequestException as error:
        print(f"❌ [Scraper] Error fetching {username}/{repo_name}: {error}")
        return None
