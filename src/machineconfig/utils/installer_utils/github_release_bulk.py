
#!/usr/bin/env python3.13
"""Script to validate installer configurations and show missing attributes."""

import json
import pathlib
import subprocess
import re
from typing import Any, Dict, List, Set
from machineconfig.utils.schemas.installer.installer_types import CPU_ARCHITECTURES, OPERATING_SYSTEMS


def find_config_files(repo_root: pathlib.Path) -> List[pathlib.Path]:
    """Find all config.json files in the repository."""
    return list(repo_root.rglob("config.json"))


def get_missing_attrs(installer: Dict[str, Any]) -> List[str]:
    """Get list of missing attributes for an installer."""
    missing_attrs: List[str] = []

    # Check required string fields
    required_strings = ["appName", "doc", "repoURL"]
    for field in required_strings:
        if field not in installer or not isinstance(installer[field], str):
            missing_attrs.append(field)

    # Check fileNamePattern structure
    if "fileNamePattern" not in installer:
        missing_attrs.append("fileNamePattern")
    else:
        pattern = installer["fileNamePattern"]
        if not isinstance(pattern, dict):
            missing_attrs.append("fileNamePattern (must be dict)")
        else:
            # Check CPU architectures
            expected_archs: Set[CPU_ARCHITECTURES] = {"amd64", "arm64"}
            actual_archs = set(pattern.keys())
            if actual_archs != expected_archs:
                missing_attrs.append(f"fileNamePattern.architectures (expected {expected_archs}, got {actual_archs})")

            # Check each architecture has OS dict
            expected_oss: Set[OPERATING_SYSTEMS] = {"windows", "linux", "macos"}
            for arch in expected_archs:
                if arch not in pattern:
                    missing_attrs.append(f"fileNamePattern.{arch}")
                elif not isinstance(pattern[arch], dict):
                    missing_attrs.append(f"fileNamePattern.{arch} (must be dict)")
                else:
                    os_dict = pattern[arch]
                    actual_oss = set(os_dict.keys())
                    if actual_oss != expected_oss:
                        missing_attrs.append(f"fileNamePattern.{arch}.oses (expected {expected_oss}, got {actual_oss})")

                    # Check each OS has string value
                    for os_name in expected_oss:
                        if os_name not in os_dict:
                            missing_attrs.append(f"fileNamePattern.{arch}.{os_name}")
                        elif not isinstance(os_dict[os_name], str):
                            missing_attrs.append(f"fileNamePattern.{arch}.{os_name} (must be string)")

    return missing_attrs


def extract_github_repo(repo_url: str) -> str | None:
    """Extract owner/repo from GitHub URL."""
    # Match https://github.com/owner/repo or git@github.com:owner/repo.git etc.
    patterns = [
        r'github\.com/([^/]+)/([^/]+?)(?:\.git)?$',
        r'git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, repo_url)
        if match:
            owner, repo = match.groups()
            return f"{owner}/{repo}"
    return None


def get_github_release_info(repo_path: str) -> str:
    """Get latest release info from GitHub API."""
    try:
        # Build curl command with optional authentication
        import os
        token = os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN')
        auth_header = f"-H 'Authorization: token {token}'" if token else ""
        
        cmd = f"curl -s {auth_header} https://api.github.com/repos/{repo_path}/releases/latest"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=pathlib.Path.cwd())
        
        if result.returncode != 0:
            return f"Error: curl failed - {result.stderr.strip()}"
        
        response = result.stdout.strip()
        if not response:
            return "Error: Empty response from API"
        
        # Check for API errors
        try:
            error_data = json.loads(response)
            if "message" in error_data:
                if "rate limit" in error_data["message"].lower():
                    return "Error: GitHub API rate limit exceeded"
                elif "not found" in error_data["message"].lower():
                    return "No releases found"
                else:
                    return f"Error: {error_data['message']}"
        except json.JSONDecodeError:
            pass  # Not an error response, continue processing
        
        # Parse the release info with robust jq
        jq_cmd = 'jq -r \'if .tag_name then .tag_name else "No tag_name" end, (if .assets and (.assets | length > 0) then (.assets[].name) else "No assets" end)\''
        jq_result = subprocess.run(f'echo \'{response}\' | {jq_cmd}', shell=True, capture_output=True, text=True)
        
        if jq_result.returncode == 0:
            return jq_result.stdout.strip()
        else:
            return f"Error: jq failed - {jq_result.stderr.strip()}"
            
    except Exception as e:
        return f"Exception: {str(e)}"


def main() -> None:
    """Main function to show missing attributes in all config.json files."""
    repo_root = pathlib.Path(__file__).parent.parent.parent.parent  # Go up to repo root
    
    output_file = repo_root / ".ai" / "tmp_scripts" / "validate_installers" / "missing_installers_report.txt"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for config_file in find_config_files(repo_root):
            try:
                with open(config_file, 'r', encoding='utf-8') as cf:
                    data = json.load(cf)

                if "installers" not in data or not isinstance(data["installers"], list):
                    continue

                for installer in data["installers"]:
                    missing_attrs = get_missing_attrs(installer)
                    # Check if any missing attrs are related to fileNamePattern
                    has_missing_filenamepattern = any("fileNamePattern" in attr for attr in missing_attrs)
                    
                    if has_missing_filenamepattern:
                        app_name = installer.get("appName", "unknown")
                        repo_url = installer.get("repoURL", "")
                        
                        f.write(f"\n{config_file.relative_to(repo_root)} - {app_name}:\n")
                        f.write(f"  Repo URL: {repo_url}\n")
                        
                        if repo_url:
                            repo_path = extract_github_repo(repo_url)
                            if repo_path:
                                f.write(f"  GitHub repo: {repo_path}\n")
                                f.write("  Latest release info:\n")
                                release_info = get_github_release_info(repo_path)
                                for line in release_info.split('\n'):
                                    if line.strip():
                                        f.write(f"    {line}\n")
                            else:
                                f.write("  Could not extract GitHub repo path from URL\n")
                        else:
                            f.write("  No repoURL found\n")

            except (json.JSONDecodeError, Exception) as e:
                f.write(f"Error processing {config_file}: {e}\n")
                continue
    
    print(f"Results written to: {output_file}")


if __name__ == "__main__":
    main()