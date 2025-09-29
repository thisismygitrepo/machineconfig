#!/usr/bin/env python3
"""
Script to fetch GitHub release information from installer JSON files.
Extracts GitHub repository URLs and fetches latest release data with rate limiting.
"""

import json
import time
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional, Set
from urllib.parse import urlparse


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


def get_repo_name_from_url(repo_url: str) -> str:
    """Extract owner/repo from GitHub URL."""
    try:
        parsed = urlparse(repo_url)
        path_parts = parsed.path.strip("/").split("/")
        return f"{path_parts[0]}/{path_parts[1]}"
    except (IndexError, AttributeError):
        return ""


def fetch_github_release_data(repo_name: str) -> Optional[Dict[str, Any]]:
    """Fetch latest release data from GitHub API using curl."""
    try:
        cmd = [
            "curl", "-s",
            f"https://api.github.com/repos/{repo_name}/releases/latest"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"❌ Failed to fetch data for {repo_name}: {result.stderr}")
            return None
            
        response_data = json.loads(result.stdout)
        
        # Check if API returned an error
        if "message" in response_data:
            if "API rate limit exceeded" in response_data.get("message", ""):
                print(f"🚫 Rate limit exceeded for {repo_name}")
                return None
            elif "Not Found" in response_data.get("message", ""):
                print(f"🔍 No releases found for {repo_name}")
                return None
                
        return response_data
        
    except (subprocess.TimeoutExpired, json.JSONDecodeError, subprocess.SubprocessError) as e:
        print(f"❌ Error fetching {repo_name}: {e}")
        return None


def extract_release_info(release_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract relevant information from GitHub release data."""
    if not release_data:
        return {}
        
    asset_names = [asset["name"] for asset in release_data.get("assets", [])]
    
    return {
        "tag_name": release_data.get("tag_name", ""),
        "name": release_data.get("name", ""),
        "published_at": release_data.get("published_at", ""),
        "assets": asset_names,
        "assets_count": len(asset_names)
    }


def main() -> None:
    """Main function to process installer JSON files and fetch GitHub release data."""
    # Define paths
    current_dir = Path(__file__).parent
    installer_dir = current_dir.parent.parent / "jobs" / "installer"
    
    standard_json = installer_dir / "installer_data.json"
    output_json = current_dir / "github_releases.json"
    
    print("🔍 Starting GitHub release data extraction...")
    print(f"📁 Processing files from: {installer_dir}")
    
    # Extract GitHub repositories from both files
    all_github_repos: Set[str] = set()
    
    if standard_json.exists():
        print(f"📄 Reading {standard_json.name}...")
        repos = extract_github_repos_from_json(standard_json)
        all_github_repos.update(repos)
        print(f"   Found {len(repos)} GitHub repos")
    else:
        print(f"⚠️  File not found: {standard_json}")    
    print(f"🎯 Total unique GitHub repositories found: {len(all_github_repos)}")
    
    if not all_github_repos:
        print("❌ No GitHub repositories found. Exiting.")
        return
    
    # Fetch release data with rate limiting
    release_mapping: Dict[str, Any] = {}
    total_repos = len(all_github_repos)
    
    print(f"\n🚀 Fetching release data for {total_repos} repositories...")
    print("⏰ Rate limiting: 5 seconds between requests")
    print("-" * 60)
    
    for i, repo_url in enumerate(sorted(all_github_repos), 1):
        repo_name = get_repo_name_from_url(repo_url)
        
        if not repo_name:
            print(f"⚠️  [{i:3d}/{total_repos}] Invalid repo URL: {repo_url}")
            continue
            
        print(f"📡 [{i:3d}/{total_repos}] Fetching: {repo_name}", end=" ... ")
        
        release_data = fetch_github_release_data(repo_name)
        
        if release_data:
            release_info = extract_release_info(release_data)
            release_mapping[repo_url] = release_info
            assets_count = release_info.get("assets_count", 0)
            tag = release_info.get("tag_name", "unknown")
            print(f"✅ {tag} ({assets_count} assets)")
        else:
            release_mapping[repo_url] = {}
            print("❌ No data")
        
        # Rate limiting - wait 5 seconds between requests (except for the last one)
        if i < total_repos:
            time.sleep(5)
    
    # Save results
    output_data = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "total_repositories": len(all_github_repos),
        "successful_fetches": len([v for v in release_mapping.values() if v]),
        "releases": release_mapping
    }
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    successful = len([v for v in release_mapping.values() if v])
    print("\n📊 Summary:")
    print(f"   Total repositories processed: {len(all_github_repos)}")
    print(f"   Successful fetches: {successful}")
    print(f"   Failed fetches: {len(all_github_repos) - successful}")
    print(f"   Output saved to: {output_json}")
    print("✅ Done!")


if __name__ == "__main__":
    main()