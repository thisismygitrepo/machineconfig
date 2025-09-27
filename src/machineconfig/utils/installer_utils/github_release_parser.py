
from typing import Optional, Any
import re
import requests
from machineconfig.utils.schemas.installer.installer_types import CPU_ARCHITECTURES, OPERATING_SYSTEMS


ARCH_PATTERNS = {
    "amd64": ["x86_64", "amd64", "x64"],
    "arm64": ["aarch64", "arm64"]
}

OS_PATTERNS = {
    "linux": ["linux", "unknown-linux", "pc-linux"],
    "macos": ["apple-darwin", "macos", "darwin"],
    "windows": ["windows", "pc-windows", "win"]
}

EXTENSIONS = {
    "linux": [".tar.gz", ".tar.xz", ".tgz"],
    "macos": [".tar.gz", ".tar.xz", ".tgz", ".dmg"],
    "windows": [".zip", ".exe", ".msi"]
}


def get_github_download_link(repo_url: str, arch: CPU_ARCHITECTURES, os: OPERATING_SYSTEMS, version: Optional[str] = None) -> Optional[str]:
    repo_match = re.search(r"github\.com[/:]([\w\-\.]+)/([\w\-\.]+)", repo_url)
    if not repo_match:
        raise ValueError(f"Invalid GitHub repo URL: {repo_url}")
    
    owner, repo = repo_match.groups()
    repo = repo.removesuffix(".git")
    
    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    
    response = requests.get(api_url)
    response.raise_for_status()
    releases: list[dict[str, Any]] = response.json()
    
    target_releases = releases
    if version is not None:
        version_clean = version.lstrip("v")
        target_releases = [
            r for r in releases 
            if r["tag_name"] == version or r["tag_name"] == f"v{version}" or r["tag_name"].lstrip("v") == version_clean
        ]
        if not target_releases:
            return None
    else:
        target_releases = [r for r in releases if not r.get("prerelease", False)]
        if not target_releases:
            target_releases = releases
    
    if not target_releases:
        return None
    
    release = target_releases[0]
    best_asset = None
    best_score = 0
    
    for asset in release["assets"]:
        filename = asset["name"].lower()
        score = 0
        
        arch_match = any(pattern in filename for pattern in ARCH_PATTERNS[arch])
        os_match = any(pattern in filename for pattern in OS_PATTERNS[os])
        ext_match = any(filename.endswith(ext) for ext in EXTENSIONS[os])
        
        if arch_match and os_match and ext_match:
            score = 1
            if os == "linux" and "musl" in filename:
                score -= 1
            score += max(0, 50 - len(asset["name"])) // 10
            
            if score > best_score:
                best_score = score
                best_asset = asset
    
    return best_asset["browser_download_url"] if best_asset else None
