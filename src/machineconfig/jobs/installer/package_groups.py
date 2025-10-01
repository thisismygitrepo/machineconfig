from typing import Literal, TypeAlias, Union

# AI/LLM Tools - AI-powered coding and chat assistants
PACKAGES_AI_TOOLS = [
    "aider",
    "github-copilot-cli",
    "gemini",
    "crush",
    "opencode-ai",
    "ollama",
    "chatgpt",
    "mods",
    "q",
    "cursor-cli",
    "droid",
    "auggie",
]

# Tunneling/Port Forwarding - Tools for exposing local services
PACKAGES_TUNNELING = [
    "ngrok",
    "devtunnel",
    "cloudflared",
    "forward-cli",
]

# Terminal Emulators & Shells - Terminal applications, emulators, and shell environments
PACKAGES_TERMINAL_EMULATORS = [
    "Alacritty",
    "Wezterm",
    "warp",
    "vtm",
    "edex-ui",
    "extraterm",
    "nushell",
]

# Browsers - Web browsers and terminal browsers
PACKAGES_BROWSERS = [
    "Brave",
    "bypass-paywalls-chrome",
    "browsh",
    "carbonyl",
]

# Code Editors & IDEs - Code editing tools
# NOTE: Entries must match the corresponding `appName` in installer_data.json for filtering to work.
PACKAGES_CODE_EDITORS = [
    "code",
    "Cursor",
    "lvim",
]

# Presentation & Text UI Tools - Markdown viewers, presentations, prompts, and text decoration
PACKAGES_PRESENTATION = [
    "patat",
    "marp",
    "presenterm",
    "glow",
    "gum",
    "boxes",
    "hx",
]

# Database Tools - Database clients and visualizers
PACKAGES_DATABASE = [
    "SqliteBrowser",
    "DBeaver",
    "rainfrog",
    "duckdb",
]

# Documentation & Conversion - Document conversion, diagram tools, and fast file operations
PACKAGES_DOC_CONVERSION = [
    "mermaid-cli",
    "html2markdown",
    "pandoc",
]

# Media & Entertainment - Music players and media tools
PACKAGES_MEDIA = [
    "ytui-music",
    "youtube-tui",
    "termusic",
    "kronos",
    "OBS Background removal",
]

# File Sharing & Cloud - File sharing, transfer, backup, sync, and QR tools
PACKAGES_FILE_SHARING = [
    "cpz",
    "rmz",
    "ffsend",
    "portal",
    "qrcp",
    "termscp",
    "filebrowser",
    "qr",
    "qrscan",
    "sharewifi",
    "share-wifi",
    "easy-sharing",
    "ezshare",
    "restic",
    "syncthing",
    "cloudreve",
    "ots",
]


# Git & Docker Tools - Version control and container utilities
PACKAGES_GIT_DOCKER_TOOLS = [
    "lazygit",
    "onefetch",
    "gitcs",
    "lazydocker",
]

# Development Tools - Various development utilities
PACKAGES_DEV_UTILS = [
    "devcontainer",
    "rust-analyzer",
    "evcxr",
    "geckodriver",
]

# Code Analysis, Git & Docs - Code analysis, statistics, documentation, and Git tools
PACKAGES_CODE_ANALYSIS = [
    "hyperfine",
    "kondo",
    "tokei",
    "navi",
    "tealdeer",
    "gitui",
    "delta",
    "gh",
]

# Productivity & Utilities - Productivity tools, security, remote access, and terminal enhancements
PACKAGES_PRODUCTIVITY = [
    "espanso",
    "bitwarden",
    "openpomodoro-cli",
    "just",
    "rustdesk",
]

# Miscellaneous Tools - Other tools
PACKAGES_MISC_DEV = [
    "Gorilla",
    "nerdfont",
    "Redis",
    "winget",
    "transmission",
    "exa",
    "bytehound",
    "atuin",
    "xcrawl3r",
    "obsidian",
    "istio",
    "cointop",
    "nnn",
]

# Main DEV package list - combines all subgroups
PACKAGES_NAMES_DEV = [
    *PACKAGES_AI_TOOLS,
    *PACKAGES_TUNNELING,
    *PACKAGES_TERMINAL_EMULATORS,
    *PACKAGES_BROWSERS,
    *PACKAGES_CODE_EDITORS,
    *PACKAGES_PRESENTATION,
    *PACKAGES_DATABASE,
    *PACKAGES_DOC_CONVERSION,
    *PACKAGES_MEDIA,
    *PACKAGES_FILE_SHARING,
    *PACKAGES_GIT_DOCKER_TOOLS,
    *PACKAGES_DEV_UTILS,
    *PACKAGES_CODE_ANALYSIS,
    *PACKAGES_PRODUCTIVITY,
    *PACKAGES_MISC_DEV,
]

# System & Network Monitoring - System resource monitors, process viewers, network analysis, and system info tools
PACKAGES_SYSTEM_MONITORS = [
    "btop",
    "btm",
    "ntop",
    "procs",
    "bandwhich",
    "ipinfo",
    "sniffnet",
    "cpufetch",
    "fastfetch",
    "topgrade",
]


# File Tools - File browsing, navigation, listing, directory jumping, and disk usage analysis
PACKAGES_FILE_TOOLS = [
    "xplr",
    "joshuto",
    "lf",
    "tere",
    "yazi",
    "lsd",
    "zoxide",
    "diskonaut",
    "dua",
    "dust",
]

# File Viewers - File preview and viewing tools
PACKAGES_FILE_VIEWERS = [
    "pistol",
    "bat",
    "viu",
]


# Search & Archive Tools - File and content search utilities, archive management
PACKAGES_SEARCH = [
    "fd",
    "fzf",
    "broot",
    "rg",
    "rga",
    "ugrep",
    "ouch",
]

# Terminal & Shell Enhancements - Terminal multiplexers, shell history, and prompts
PACKAGES_TERMINAL_SHELL = [
    "zellij",
    "mprocs",
    "mcfly",
    "starship",
    "lolcatjs",
    "figlet-cli",
]
# Web Sharing - Share terminal over web
PACKAGES_WEB_TERMINAL = [
    "gotty",
    "ttyd",
]


# Cloud & Utilities - Cloud storage, file watching, web terminal, and presentation tools
PACKAGES_CLOUD_UTILS = [
    "rclone",
    "watchexec",
    "m365",
    "zoomit",
    "speedtest",
]




# Main ESSENTIAL package list - combines all subgroups
PACKAGES_NAMES_ESSENTIAL = [
    *PACKAGES_CODE_ANALYSIS,
    *PACKAGES_PRESENTATION,
    *PACKAGES_FILE_VIEWERS,
    *PACKAGES_FILE_TOOLS,
    *PACKAGES_SYSTEM_MONITORS,
    *PACKAGES_WEB_TERMINAL,
    *PACKAGES_TERMINAL_SHELL,
    *PACKAGES_SEARCH,
    *PACKAGES_AI_TOOLS,
    *PACKAGES_CLOUD_UTILS,
]

PACKAGE_GROUPS: TypeAlias = Literal[
    "ESSENTIAL",
    "DEV",
    "AI_TOOLS",
    "TUNNELING",
    "TERMINAL_EMULATORS",
    "BROWSERS",
    "CODE_EDITORS",
    "PRESENTATION",
    "DATABASE",
    "DOC_CONVERSION",
    "MEDIA",
    "FILE_SHARING",
    "GIT_DOCKER_TOOLS",
    "DEV_UTILS",
    "CODE_ANALYSIS",
    "PRODUCTIVITY",
    "MISC_DEV",
    "SYSTEM_MONITORS",
    "FILE_TOOLS",
    "FILE_VIEWERS",
    "SEARCH",
    "TERMINAL_SHELL",
    "CLOUD_UTILS",
    "WEB_TERMINAL",
]
PACKAGE_GROUP2NAMES: dict[PACKAGE_GROUPS, list[str]] = {
    "ESSENTIAL": PACKAGES_NAMES_ESSENTIAL,
    "DEV": PACKAGES_NAMES_DEV,
    "AI_TOOLS": PACKAGES_AI_TOOLS,
    "TUNNELING": PACKAGES_TUNNELING,
    "TERMINAL_EMULATORS": PACKAGES_TERMINAL_EMULATORS,
    "BROWSERS": PACKAGES_BROWSERS,
    "CODE_EDITORS": PACKAGES_CODE_EDITORS,
    "PRESENTATION": PACKAGES_PRESENTATION,
    "DATABASE": PACKAGES_DATABASE,
    "DOC_CONVERSION": PACKAGES_DOC_CONVERSION,
    "MEDIA": PACKAGES_MEDIA,
    "FILE_SHARING": PACKAGES_FILE_SHARING,
    "GIT_DOCKER_TOOLS": PACKAGES_GIT_DOCKER_TOOLS,
    "DEV_UTILS": PACKAGES_DEV_UTILS,
    "CODE_ANALYSIS": PACKAGES_CODE_ANALYSIS,
    "PRODUCTIVITY": PACKAGES_PRODUCTIVITY,
    "MISC_DEV": PACKAGES_MISC_DEV,
    "SYSTEM_MONITORS": PACKAGES_SYSTEM_MONITORS,
    "FILE_TOOLS": PACKAGES_FILE_TOOLS,
    "FILE_VIEWERS": PACKAGES_FILE_VIEWERS,
    "SEARCH": PACKAGES_SEARCH,
    "TERMINAL_SHELL": PACKAGES_TERMINAL_SHELL,
    "CLOUD_UTILS": PACKAGES_CLOUD_UTILS,
    "WEB_TERMINAL": PACKAGES_WEB_TERMINAL,
}

_ = Union, Literal
