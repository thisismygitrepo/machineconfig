
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
    "linux": [".tar.gz", ".tar.xz", ".tgz", ".zip", ".deb", ".rpm", ".AppImage", ""],  # Allow no extension
    "macos": [".tar.gz", ".tar.xz", ".tgz", ".dmg", ".zip", ""],  # Allow no extension
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
        
        # Check extension match - handle empty string (no extension) specially
        ext_match = False
        for ext in EXTENSIONS[os]:
            if ext == "":  # No extension case
                # Check if filename doesn't end with any known extension
                known_extensions = [".tar.gz", ".tar.xz", ".tgz", ".zip", ".deb", ".rpm", ".AppImage", ".dmg", ".exe", ".msi"]
                if not any(filename.endswith(known_ext) for known_ext in known_extensions):
                    ext_match = True
                    break
            elif filename.endswith(ext):
                ext_match = True
                break
        
        # Special case: if no explicit architecture in filename but OS matches,
        # assume it's for the most common architecture (amd64) if that's what we're looking for
        if not arch_match and arch == "amd64" and os_match and ext_match:
            # Check if filename doesn't contain any other architecture indicators
            other_archs = [pattern for other_arch, patterns in ARCH_PATTERNS.items() 
                          if other_arch != arch for pattern in patterns]
            if not any(other_arch_pattern in filename for other_arch_pattern in other_archs):
                arch_match = True
                score = 8  # Slightly lower score than explicit arch match
        
        # Special case: if arch matches but no OS pattern found, and it's a simple binary (no extension),
        # assume it's for Linux if that's what we're looking for
        if arch_match and not os_match and os == "linux" and ext_match:
            # Check if filename doesn't contain Windows/Mac specific indicators
            non_linux_indicators = ["win", "windows", "exe", "msi", "macos", "darwin", "dmg"]
            if not any(indicator in filename for indicator in non_linux_indicators):
                os_match = True
                score = 8  # Slightly lower score than explicit OS match
        
        if arch_match and os_match and ext_match:
            score = max(score, 10)  # Base score for matching all criteria
            
            # Prefer glibc over musl, but don't exclude musl
            if os == "linux":
                if "musl" in filename:
                    score += 1  # musl is still acceptable
                else:
                    score += 2  # prefer glibc when available
                
                # Prefer portable formats over package manager specific ones
                if filename.endswith((".tar.gz", ".tar.xz", ".tgz")):
                    score += 3  # Most portable
                elif filename.endswith(".zip"):
                    score += 2  # Also portable
                elif filename.endswith(".deb"):
                    score += 1  # Package manager specific but common
            
            # Prefer shorter names (less verbose usually means more standard)
            score += max(0, 50 - len(asset["name"])) // 10
            
            if score > best_score:
                best_score = score
                best_asset = asset
    
    if best_asset:
        return best_asset["browser_download_url"]
    else:
        # Print all available release binary names and matching details before returning None
        all_asset_names = [asset["name"] for asset in release["assets"]]
        print(f"No suitable binary found for {arch}/{os}. Available release binaries:")
        for i, name in enumerate(all_asset_names, 1):
            print(f"  {i}. {name}")
        
        # Debug: Show which patterns we're looking for
        print(f"\nLooking for patterns:")
        print(f"  Architecture patterns for '{arch}': {ARCH_PATTERNS[arch]}")
        print(f"  OS patterns for '{os}': {OS_PATTERNS[os]}")
        print(f"  Extension patterns for '{os}': {EXTENSIONS[os]}")
        
        # Debug: Show why each asset didn't match
        print(f"\nDebug matching details:")
        for asset in release["assets"]:
            filename = asset["name"].lower()
            arch_match = any(pattern in filename for pattern in ARCH_PATTERNS[arch])
            os_match = any(pattern in filename for pattern in OS_PATTERNS[os])
            # Use the same extension matching logic as in the main loop
            ext_match = False
            for ext in EXTENSIONS[os]:
                if ext == "":  # No extension case
                    # Check if filename doesn't end with any known extension
                    known_extensions = [".tar.gz", ".tar.xz", ".tgz", ".zip", ".deb", ".rpm", ".AppImage", ".dmg", ".exe", ".msi"]
                    if not any(filename.endswith(known_ext) for known_ext in known_extensions):
                        ext_match = True
                        break
                elif filename.endswith(ext):
                    ext_match = True
                    break
            print(f"  {asset['name']}: arch={arch_match}, os={os_match}, ext={ext_match}")
        
        return None
