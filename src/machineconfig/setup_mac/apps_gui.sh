#!/usr/bin/env bash

# macOS GUI Application Installation Script
# Comprehensive GUI application installation via Homebrew Cask and Mac App Store
# Supports Intel and Apple Silicon architectures

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Architecture detection
detect_architecture() {
    local arch=$(uname -m)
    if [[ "$arch" == "arm64" ]]; then
        echo "arm64"
    elif [[ "$arch" == "x86_64" ]]; then
        echo "amd64"
    else
        log_warning "Unknown architecture: $arch, defaulting to amd64"
        echo "amd64"
    fi
}

# Check if Homebrew is installed
check_homebrew() {
    if ! command -v brew &> /dev/null; then
        log_error "Homebrew is not installed. Please run apps.sh first to install Homebrew."
        exit 1
    fi
    log_success "Homebrew found"
}

# Setup Mac App Store CLI
setup_mas() {
    log_info "Setting up Mac App Store CLI (mas)..."
    
    if ! command -v mas &> /dev/null; then
        log_info "Installing mas (Mac App Store CLI)..."
        brew install mas || {
            log_error "Failed to install mas"
            return 1
        }
    else
        log_success "mas already installed"
    fi
    
    # Check if user is signed in to Mac App Store
    if ! mas account &> /dev/null; then
        log_warning "Not signed in to Mac App Store. Some applications may not install."
        log_info "Please sign in to the Mac App Store manually to install App Store applications."
    else
        log_success "Signed in to Mac App Store"
    fi
}

# Install a GUI application with error handling
install_gui_app() {
    local app_name="$1"
    local description="$2"
    local install_cmd="$3"
    local fallback_cmd="$4"
    
    log_info "Installing $description..."
    
    if eval "$install_cmd"; then
        log_success "$app_name installed successfully"
        return 0
    elif [[ -n "$fallback_cmd" ]]; then
        log_warning "Primary installation failed, trying fallback method..."
        if eval "$fallback_cmd"; then
            log_success "$app_name installed via fallback method"
            return 0
        else
            log_error "Failed to install $app_name via fallback method"
            return 1
        fi
    else
        log_error "Failed to install $app_name"
        return 1
    fi
}

# Install GUI applications from a list
install_gui_app_list() {
    local group_name="$1"
    shift
    local apps=("$@")
    
    log_info "Installing $group_name applications..."
    
    local failed_apps=()
    for app_info in "${apps[@]}"; do
        IFS='|' read -r app_name description install_cmd fallback_cmd <<< "$app_info"
        if ! install_gui_app "$app_name" "$description" "$install_cmd" "$fallback_cmd"; then
            failed_apps+=("$app_name")
        fi
    done
    
    if [[ ${#failed_apps[@]} -gt 0 ]]; then
        log_warning "$group_name: Failed to install: ${failed_apps[*]}"
    else
        log_success "All $group_name applications installed successfully"
    fi
}

# Main installation function
main() {
    log_info "Starting macOS GUI application installation..."
    log_info "Detected architecture: $(detect_architecture)"
    
    # Check prerequisites
    check_homebrew
    setup_mas
    
    # --GROUP:BROWSERS - Web browsers
    local browsers=(
        "brave-browser|Brave Browser - Privacy-focused web browser|brew install --cask brave-browser|"
        "google-chrome|Google Chrome web browser|brew install --cask google-chrome|"
        "firefox|Mozilla Firefox web browser|brew install --cask firefox|"
        "microsoft-edge|Microsoft Edge web browser|brew install --cask microsoft-edge|"
        "safari-technology-preview|Safari Technology Preview|brew install --cask safari-technology-preview|"
    )
    
    install_gui_app_list "Browsers" "${browsers[@]}"
    
    # --GROUP:CODE_EDITORS - Code editors and IDEs
    local code_editors=(
        "visual-studio-code|Visual Studio Code|brew install --cask visual-studio-code|"
        "cursor|Cursor AI-powered code editor|brew install --cask cursor|"
        "sublime-text|Sublime Text editor|brew install --cask sublime-text|"
        "atom|Atom text editor|brew install --cask atom|"
        "webstorm|JetBrains WebStorm IDE|brew install --cask webstorm|"
        "pycharm|JetBrains PyCharm IDE|brew install --cask pycharm|"
        "intellij-idea|JetBrains IntelliJ IDEA|brew install --cask intellij-idea|"
        "xcode|Xcode development environment|mas install 497799835|brew install --cask xcode"
    )
    
    install_gui_app_list "Code Editors & IDEs" "${code_editors[@]}"
    
    # --GROUP:PRODUCTIVITY - Productivity and office applications
    local productivity=(
        "obsidian|Obsidian note-taking app|brew install --cask obsidian|"
        "notion|Notion workspace|brew install --cask notion|"
        "bitwarden|Bitwarden password manager|brew install --cask bitwarden|"
        "1password|1Password password manager|brew install --cask 1password|mas install 1333542190"
        "alfred|Alfred productivity app|brew install --cask alfred|"
        "raycast|Raycast launcher and productivity tool|brew install --cask raycast|"
        "rectangle|Rectangle window management|brew install --cask rectangle|"
        "magnet|Magnet window manager|mas install 441258766|brew install --cask magnet"
        "cleanmymac|CleanMyMac X system cleaner|mas install 1339170533|"
    )
    
    install_gui_app_list "Productivity" "${productivity[@]}"
    
    # --GROUP:MEDIA - Media and entertainment applications
    local media=(
        "vlc|VLC media player|brew install --cask vlc|"
        "obs|OBS Studio for streaming and recording|brew install --cask obs|"
        "handbrake|HandBrake video transcoder|brew install --cask handbrake|"
        "spotify|Spotify music streaming|brew install --cask spotify|mas install 324684580"
        "youtube-music|YouTube Music|brew install --cask youtube-music|"
        "plex|Plex media server|brew install --cask plex|"
        "keka|Keka archive utility|brew install --cask keka|mas install 470158793"
        "the-unarchiver|The Unarchiver|brew install --cask the-unarchiver|mas install 425424353"
    )
    
    install_gui_app_list "Media & Entertainment" "${media[@]}"
    
    # --GROUP:DEVELOPMENT - Development and system tools
    local development=(
        "docker|Docker Desktop|brew install --cask docker|"
        "postman|Postman API development|brew install --cask postman|"
        "insomnia|Insomnia REST client|brew install --cask insomnia|"
        "github-desktop|GitHub Desktop|brew install --cask github-desktop|"
        "sourcetree|Sourcetree Git client|brew install --cask sourcetree|"
        "iterm2|iTerm2 terminal emulator|brew install --cask iterm2|"
        "warp|Warp modern terminal|brew install --cask warp|"
        "alacritty|Alacritty terminal emulator|brew install --cask alacritty|"
    )
    
    install_gui_app_list "Development Tools" "${development[@]}"
    
    # --GROUP:DATABASE - Database management tools
    local database=(
        "dbeaver-community|DBeaver database tool|brew install --cask dbeaver-community|"
        "sequel-pro|Sequel Pro MySQL client|brew install --cask sequel-pro|"
        "tableplus|TablePlus database client|brew install --cask tableplus|"
        "redis-insight|RedisInsight Redis GUI|brew install --cask redisinsight|"
        "mongodb-compass|MongoDB Compass|brew install --cask mongodb-compass|"
    )
    
    install_gui_app_list "Database Tools" "${database[@]}"
    
    # --GROUP:COMMUNICATION - Communication and collaboration
    local communication=(
        "slack|Slack team communication|brew install --cask slack|mas install 803453959"
        "discord|Discord voice and text chat|brew install --cask discord|"
        "zoom|Zoom video conferencing|brew install --cask zoom|"
        "microsoft-teams|Microsoft Teams|brew install --cask microsoft-teams|"
        "whatsapp|WhatsApp Desktop|brew install --cask whatsapp|mas install 1147396723"
        "telegram|Telegram messaging|brew install --cask telegram|mas install 747648890"
    )
    
    install_gui_app_list "Communication" "${communication[@]}"
    
    # --GROUP:SYSTEM_UTILITIES - System utilities and maintenance
    local system_utilities=(
        "appcleaner|AppCleaner uninstaller|brew install --cask appcleaner|"
        "coconutbattery|CoconutBattery system info|brew install --cask coconutbattery|"
        "disk-utility|Disk Utility (built-in)|echo 'Disk Utility is built into macOS'|"
        "activity-monitor|Activity Monitor (built-in)|echo 'Activity Monitor is built into macOS'|"
        "finder|Finder (built-in)|echo 'Finder is built into macOS'|"
        "homebrew|Homebrew package manager|echo 'Homebrew already installed'|"
    )
    
    install_gui_app_list "System Utilities" "${system_utilities[@]}"
    
    log_success "macOS GUI application installation completed!"
    log_info "Some applications may require additional setup or signing in to your accounts."
    log_info "Check Applications folder for newly installed apps."
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi