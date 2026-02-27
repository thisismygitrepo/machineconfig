

from dataclasses import dataclass
from typing import Any
import json
import re
import urllib.error
import urllib.request


GITHUB_API_BASE: str = "https://api.github.com"
USER_AGENT: str = "machineconfig-skill/make-github-installer-config"


@dataclass(frozen=True)
class RepoSpec:
    owner: str
    repo: str


@dataclass(frozen=True)
class ReleaseAsset:
    name: str


@dataclass(frozen=True)
class ReleaseInfo:
    tag_name: str
    assets: list[ReleaseAsset]


def parse_repo_url(repo_url: str) -> RepoSpec:
    cleaned: str = repo_url.strip().removesuffix("/")
    match = re.match(r"^https?://github\.com/(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+)$", cleaned)
    if match is None:
        raise ValueError(f"Invalid GitHub repository URL: {repo_url}")
    owner: str = match.group("owner")
    repo: str = match.group("repo")
    return RepoSpec(owner=owner, repo=repo)


def _http_get_json(url: str) -> Any:
    request = urllib.request.Request(url=url, headers={"Accept": "application/vnd.github+json", "User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"GitHub API HTTP error {error.code} for URL: {url}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"Network error while requesting GitHub API URL: {url}") from error
    return json.loads(data)


def fetch_releases(spec: RepoSpec, limit: int) -> list[ReleaseInfo]:
    if limit <= 0:
        raise ValueError("limit must be positive")
    api_url: str = f"{GITHUB_API_BASE}/repos/{spec.owner}/{spec.repo}/releases?per_page={limit}"
    payload: Any = _http_get_json(api_url)
    if not isinstance(payload, list):
        raise RuntimeError("Unexpected GitHub API response format for releases endpoint")

    releases: list[ReleaseInfo] = []
    for release_row in payload:
        if not isinstance(release_row, dict):
            continue
        tag_name_raw: Any = release_row.get("tag_name")
        assets_raw: Any = release_row.get("assets")
        if not isinstance(tag_name_raw, str):
            continue
        assets: list[ReleaseAsset] = []
        if isinstance(assets_raw, list):
            for asset_row in assets_raw:
                if not isinstance(asset_row, dict):
                    continue
                asset_name: Any = asset_row.get("name")
                if isinstance(asset_name, str):
                    assets.append(ReleaseAsset(name=asset_name))
        releases.append(ReleaseInfo(tag_name=tag_name_raw, assets=assets))

    if len(releases) == 0:
        raise RuntimeError(f"No releases found for {spec.owner}/{spec.repo}")
    return releases


def normalize_version_for_placeholder(tag_name: str) -> str:
    return tag_name[1:] if tag_name.startswith("v") else tag_name


def classify_os(asset_name: str) -> str | None:
    lowered: str = asset_name.lower()
    if "linux" in lowered:
        return "linux"
    if "darwin" in lowered or "macos" in lowered or "apple" in lowered or "osx" in lowered:
        return "macos"
    if "windows" in lowered or "win" in lowered or "msvc" in lowered:
        return "windows"
    return None


def classify_arch(asset_name: str) -> str | None:
    lowered: str = asset_name.lower()
    if "aarch64" in lowered or "arm64" in lowered:
        return "arm64"
    if "x86_64" in lowered or "amd64" in lowered or "x64" in lowered:
        return "amd64"
    return None


def looks_like_binary_asset(asset_name: str) -> bool:
    lowered: str = asset_name.lower()
    excluded_tokens: tuple[str, ...] = ("checksums", "sha256", ".sig", ".pem", "sbom", ".txt", ".json")
    if any(token in lowered for token in excluded_tokens):
        return False
    archive_like: tuple[str, ...] = (".tar.gz", ".tgz", ".tar.xz", ".zip", ".7z", ".exe", ".msi", ".pkg", ".deb", ".rpm")
    return any(lowered.endswith(suffix) for suffix in archive_like)


def to_placeholder_pattern(asset_name: str, tag_name: str) -> str:
    tag_no_v: str = normalize_version_for_placeholder(tag_name)
    variants: list[str] = [tag_name, tag_no_v, f"v{tag_no_v}"]
    variants_sorted: list[str] = sorted(set(variants), key=len, reverse=True)
    result: str = asset_name
    for variant in variants_sorted:
        if len(variant) == 0:
            continue
        result = result.replace(variant, "{version}")
    return result


def file_exists_for_pattern(asset_names: set[str], pattern: str, latest_tag_name: str) -> bool:
    normalized_version: str = normalize_version_for_placeholder(latest_tag_name)
    candidate_a: str = pattern.replace("{version}", normalized_version)
    candidate_b: str = pattern.replace("{version}", latest_tag_name)
    return candidate_a in asset_names or candidate_b in asset_names
