
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional
from urllib.parse import urlparse

import csv
import io
import sys

import requests
from machineconfig.utils.io import read_json


def get_gh_token() -> str:
    from machineconfig.utils.io import read_ini
    ini = read_ini(Path.home().joinpath("dotfiles/creds/git/git_host_tokens.ini"))
    token = ini.get("thisismygitrepo", "newLongterm", fallback=None)
    if token is None:
        raise RuntimeError("GitHub token not found in creds.")
    return token


@dataclass(frozen=True)
class RepoSpec:
    owner: str
    name: str


@dataclass(frozen=True)
class LicenseCandidate:
    path: str
    url: str


@dataclass(frozen=True)
class LicenseFetchResult:
    candidate: Optional[LicenseCandidate]
    status: str
    detail: str
    license_name: str


@dataclass(frozen=True)
class RepoResult:
    owner: str
    name: str
    status: str
    license_path: str
    license_name: str
    download_url: str
    saved_path: str
    detail: str


def _load_installers(installer_data_path: Path) -> list[dict[str, Any]]:
    data = read_json(path=installer_data_path)
    installers = data.get("installers")
    if not isinstance(installers, list):
        raise ValueError(f"installers list missing in {installer_data_path}")
    return installers


def _extract_github_specs(installers: Iterable[dict[str, Any]]) -> list[RepoSpec]:
    specs: list[RepoSpec] = []
    for installer in installers:
        repo_url = installer.get("repoURL")
        if not isinstance(repo_url, str):
            continue
        repo_url_lower = repo_url.lower()
        if "github" not in repo_url_lower:
            continue
        parsed = urlparse(repo_url)
        if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
            continue
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) < 2:
            continue
        owner = parts[0]
        name = parts[1]
        if name.endswith(".git"):
            name = name[:-4]
        if not owner or not name:
            continue
        specs.append(RepoSpec(owner=owner, name=name))
    deduped: dict[tuple[str, str], RepoSpec] = {}
    for spec in specs:
        deduped[(spec.owner.lower(), spec.name.lower())] = spec
    return list(deduped.values())


def _default_headers(token: str) -> dict[str, str]:
    return {
        "User-Agent": "machineconfig-license-fetcher",
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _is_license_filename(file_name: str) -> bool:
    lower = file_name.casefold()
    return "license" in lower or "licence" in lower


def _filter_root_license_candidates(candidates: list[LicenseCandidate]) -> list[LicenseCandidate]:
    filtered: list[LicenseCandidate] = []
    for candidate in candidates:
        if "/" in candidate.path:
            continue
        if not _is_license_filename(candidate.path):
            continue
        filtered.append(candidate)
    return filtered


def _download_license(candidate: LicenseCandidate, session: requests.Session, timeout: float, target_path: Path) -> bool:
    try:
        response = session.get(candidate.url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException:
        return False
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(response.text, encoding="utf-8")
    return True


def _resolve_repo_root() -> Path:
    from machineconfig.utils.source_of_truth import REPO_ROOT
    repo_root = REPO_ROOT
    return repo_root


def _resolve_installer_data_path(repo_root: Path) -> Path:
    return repo_root / "src" / "machineconfig" / "jobs" / "installer" / "installer_data.json"


def _resolve_output_dir(repo_root: Path, repo_name: str) -> Path:
    return repo_root / ".ai" / "repos" / repo_name


def _select_license_candidate(candidates: list[LicenseCandidate]) -> Optional[LicenseCandidate]:
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    def _priority(candidate: LicenseCandidate) -> tuple[int, int, str]:
        name = candidate.path.casefold()
        if name in {"license", "licence"}:
            score = 0
        elif name.startswith("license") or name.startswith("licence"):
            score = 1
        elif _is_license_filename(name):
            score = 2
        else:
            score = 3
        return (score, len(candidate.path), candidate.path)

    return min(candidates, key=_priority)


def _fetch_license_candidate(owner: str, name: str, session: requests.Session, timeout: float) -> LicenseFetchResult:
    license_api_url = f"https://api.github.com/repos/{owner}/{name}/license"
    try:
        response = session.get(license_api_url, timeout=timeout)
    except requests.RequestException:
        return LicenseFetchResult(candidate=None, status="fetch_failed", detail="license_api_unavailable", license_name="")
    if response.status_code == 404:
        return LicenseFetchResult(candidate=None, status="license_not_found", detail="license_api_404", license_name="")
    if response.status_code == 403:
        return LicenseFetchResult(candidate=None, status="rate_limited", detail="license_api_forbidden", license_name="")
    if response.status_code >= 400:
        return LicenseFetchResult(
            candidate=None,
            status="fetch_failed",
            detail=f"license_api_status_{response.status_code}",
            license_name="",
        )
    try:
        payload = response.json()
    except ValueError:
        return LicenseFetchResult(candidate=None, status="fetch_failed", detail="license_api_invalid_json", license_name="")
    if not isinstance(payload, dict):
        return LicenseFetchResult(candidate=None, status="fetch_failed", detail="license_api_invalid_payload", license_name="")
    path_value = payload.get("path")
    download_url_value = payload.get("download_url")
    license_payload = payload.get("license")
    license_name_value = ""
    if isinstance(license_payload, dict):
        license_name = license_payload.get("name")
        if isinstance(license_name, str):
            license_name_value = license_name
    if not isinstance(path_value, str) or not isinstance(download_url_value, str):
        return LicenseFetchResult(candidate=None, status="license_not_found", detail="license_api_missing_fields", license_name=license_name_value)
    candidate = LicenseCandidate(path=path_value, url=download_url_value)
    root_candidates = _filter_root_license_candidates([candidate])
    selected = _select_license_candidate(root_candidates)
    if selected is None:
        return LicenseFetchResult(candidate=None, status="license_not_found", detail="no_root_license_match", license_name=license_name_value)
    return LicenseFetchResult(candidate=selected, status="ok", detail="", license_name=license_name_value)


def run_download() -> None:
    repo_root = _resolve_repo_root()
    installer_path = _resolve_installer_data_path(repo_root)
    csv_path = installer_path.with_name(f"{installer_path.stem}_licenses.csv")
    installers = _load_installers(installer_path)
    specs = _extract_github_specs(installers)
    session = requests.Session()
    token = get_gh_token()
    session.headers.update(_default_headers(token=token))
    timeout = 20.0
    results: list[RepoResult] = []
    total = len(specs)
    print(f"Starting license fetch for {total} repositories.", file=sys.stderr, flush=True)
    for idx, spec in enumerate(specs, start=1):
        print(f"[{idx}/{total}] Fetching license metadata for {spec.owner}/{spec.name}", file=sys.stderr, flush=True)
        fetch_result = _fetch_license_candidate(owner=spec.owner, name=spec.name, session=session, timeout=timeout)
        if fetch_result.candidate is None:
            print(
                f"[{idx}/{total}] {spec.owner}/{spec.name} -> {fetch_result.status}",
                file=sys.stderr,
                flush=True,
            )
            results.append(
                RepoResult(
                    owner=spec.owner,
                    name=spec.name,
                    status=fetch_result.status,
                    license_path="",
                    license_name=fetch_result.license_name,
                    download_url="",
                    saved_path="",
                    detail=fetch_result.detail,
                )
            )
            continue
        candidate = fetch_result.candidate
        target_dir = _resolve_output_dir(repo_root, spec.name)
        target_file = target_dir / Path(candidate.path).name
        print(
            f"[{idx}/{total}] Downloading license file {candidate.path} for {spec.owner}/{spec.name}",
            file=sys.stderr,
            flush=True,
        )
        if _download_license(candidate=candidate, session=session, timeout=timeout, target_path=target_file):
            print(
                f"[{idx}/{total}] Saved -> {target_file}",
                file=sys.stderr,
                flush=True,
            )
            results.append(
                RepoResult(
                    owner=spec.owner,
                    name=spec.name,
                    status="saved",
                    license_path=candidate.path,
                    license_name=fetch_result.license_name,
                    download_url=candidate.url,
                    saved_path=str(target_file),
                    detail="",
                )
            )
        else:
            print(
                f"[{idx}/{total}] Download failed for {spec.owner}/{spec.name}",
                file=sys.stderr,
                flush=True,
            )
            results.append(
                RepoResult(
                    owner=spec.owner,
                    name=spec.name,
                    status="download_failed",
                    license_path=candidate.path,
                    license_name=fetch_result.license_name,
                    download_url=candidate.url,
                    saved_path=str(target_file),
                    detail="download_error",
                )
            )
    print("Building CSV summary.", file=sys.stderr, flush=True)
    csv_output = io.StringIO()
    writer = csv.writer(csv_output)
    writer.writerow(["owner", "name", "status", "license_path", "license_name", "download_url", "saved_path", "detail"])
    for result in results:
        writer.writerow(
            [
                result.owner,
                result.name,
                result.status,
                result.license_path,
                result.license_name,
                result.download_url,
                result.saved_path,
                result.detail,
            ]
        )
    csv_path.write_text(csv_output.getvalue(), encoding="utf-8")
    print(csv_output.getvalue(), end="")


if __name__ == "__main__":
    run_download()
