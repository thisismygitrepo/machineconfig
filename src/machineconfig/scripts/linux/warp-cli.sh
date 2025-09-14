#!/usr/bin/env bash
# Installs Cloudflare WARP (warp-cli) on supported Ubuntu / Debian systems.
# Usage: sudo ./warp-cli.sh [--allow-unsupported] [--force-reinstall]

set -euo pipefail

ALLOW_UNSUPPORTED=0
FORCE_REINSTALL=0

for arg in "$@"; do
  case "$arg" in
    --allow-unsupported) ALLOW_UNSUPPORTED=1 ;;
    --force-reinstall) FORCE_REINSTALL=1 ;;
    -h|--help)
      printf "Usage: %s [--allow-unsupported] [--force-reinstall]\n" "$0"
      exit 0
      ;;
    *)
      printf "Unknown argument: %s\n" "$arg" >&2
      exit 2
      ;;
  esac
done

require_root() {
  if [ "${EUID}" -ne 0 ]; then
    printf "Please run as root (use sudo).\n" >&2
    exit 1
  fi
}

have_cmd() { command -v "$1" >/dev/null 2>&1; }

detect_os() {
  if have_cmd lsb_release; then
    DIST_ID=$(lsb_release -si 2>/dev/null | tr '[:upper:]' '[:lower:]')
    CODENAME=$(lsb_release -sc 2>/dev/null | tr '[:upper:]' '[:lower:]')
  elif [ -f /etc/os-release ]; then
    # shellcheck disable=SC1091
    . /etc/os-release
    DIST_ID=$(printf "%s" "${ID:-}" | tr '[:upper:]' '[:lower:]')
    CODENAME=$(printf "%s" "${VERSION_CODENAME:-}" | tr '[:upper:]' '[:lower:]')
  else
    printf "Cannot detect distribution. Install lsb_release or provide /etc/os-release.\n" >&2
    exit 1
  fi
}

is_supported() {
  case "$DIST_ID" in
    ubuntu)
      # Supported: noble jammy focal (older: bionic xenial)
      case "$CODENAME" in
        noble|jammy|focal|bionic|xenial) return 0 ;; esac ;;
    debian)
      # Supported: bookworm bullseye buster (older: stretch)
      case "$CODENAME" in
        bookworm|bullseye|buster|stretch) return 0 ;; esac ;;
  esac
  return 1
}

add_key() {
  local key_path="/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg"
  if [ -s "$key_path" ]; then
    return 0
  fi
  curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | gpg --yes --dearmor --output "$key_path"
}

add_repo() {
  local list_file="/etc/apt/sources.list.d/cloudflare-client.list"
  if grep -q "pkg.cloudflareclient.com" "$list_file" 2>/dev/null; then
    return 0
  fi
  echo "deb [signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ ${CODENAME} main" > "$list_file"
}

need_update=0
install_package() {
  if dpkg -s cloudflare-warp >/dev/null 2>&1; then
    if [ "$FORCE_REINSTALL" -eq 1 ]; then
      apt-get install --reinstall -y cloudflare-warp
    else
      printf "cloudflare-warp already installed. Use --force-reinstall to reinstall.\n"
    fi
  else
    apt-get install -y cloudflare-warp
  fi
}

main() {
  require_root
  if ! have_cmd apt-get; then
    printf "apt-get not found. This script supports only Debian/Ubuntu.\n" >&2
    exit 1
  fi
  detect_os
  if ! is_supported; then
    if [ "$ALLOW_UNSUPPORTED" -ne 1 ]; then
      printf "Distribution %s (%s) not in supported list. Use --allow-unsupported to proceed.\n" "$DIST_ID" "$CODENAME" >&2
      exit 3
    else
      printf "Proceeding on unsupported distribution %s (%s).\n" "$DIST_ID" "$CODENAME"
    fi
  fi
  pre_key_checksum=$( [ -f /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg ] && sha256sum /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg | cut -d' ' -f1 || true )
  add_key
  post_key_checksum=$(sha256sum /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg | cut -d' ' -f1)
  if [ "$pre_key_checksum" != "$post_key_checksum" ]; then need_update=1; fi
  repo_before=$(grep -R "pkg.cloudflareclient.com" /etc/apt/sources.list.d 2>/dev/null || true)
  add_repo
  repo_after=$(grep -R "pkg.cloudflareclient.com" /etc/apt/sources.list.d 2>/dev/null || true)
  if [ "$repo_before" != "$repo_after" ]; then need_update=1; fi
  if [ "$need_update" -eq 1 ]; then
    apt-get update
  fi
  install_package
  printf "Done. Basic usage: 'warp-cli register' then 'warp-cli connect'. For account: 'warp-cli set-mode warp'.\n"
}

main "$@"
