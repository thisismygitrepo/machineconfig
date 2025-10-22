from typing import Literal, TypeAlias, Union

# AI/LLM Tools - AI-powered coding and chat assistants
AGENTS = [
    "aider",
    "copilot",
    "gemini",
    "crush",
    "opencode-ai",
    "ollama",
    "chatgpt",
    "mods",
    "q",
    "qwen-code",
    "cursor-cli",
    "droid",
    "kilocode",
    "cline",
    "auggie",
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
    "m365",
    "zoomit",
]

# Code Editors & IDEs - Code editing tools
# NOTE: Entries must match the corresponding `appName` in installer_data.json for filtering to work.
PACKAGES_CODE_EDITORS = [
    "code",
    "Cursor",
    "lvim",
]



# Database Tools - Database clients and visualizers
PACKAGES_DATABASE = [
    "SqliteBrowser",
    "DBeaver",
    "rainfrog",
    "duckdb",
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
    "ngrok",
    "devtunnel",
    "cloudflared",
    "forward-cli",
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


# Development Tools - Various development utilities
PACKAGES_DEV_UTILS = [
    "devcontainer",
    "rust-analyzer",
    "evcxr",
    "geckodriver",
]

# Code Analysis, Git & Docs - Code analysis, statistics, documentation, and Git tools
PACKAGES_CODE_ANALYSIS = [
    "lazygit",
    "onefetch",
    "gitcs",
    "lazydocker",
    "hyperfine",
    "kondo",
    "tokei",
    "navi",
    "tealdeer",
    "gitui",
    "delta",
    "gh",
    "watchexec",
    "jq",
]

# Productivity & Utilities - Productivity tools, security, remote access, and terminal enhancements
PACKAGES_PRODUCTIVITY = [
    "espanso",
    "bitwarden",
    "openpomodoro-cli",
    "rustdesk",
    "mermaid-cli",
    "html2markdown",
    "pandoc",
    "patat",
    "marp",
    "presenterm",
    "glow",
    "gum",
    "hx",
]

# Miscellaneous Tools - Other tools
PACKAGES_MISC_DEV = [
    "lolcatjs",
    "figlet-cli",
    "boxes",
    "Gorilla",
    "Redis",
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
    "speedtest",
]




# Search & Archive Tools - File and content search utilities, archive management
PACKAGES_FILE = [
    "nerdfont",
    "winget",
    "fd",
    "fzf",
    "broot",
    "rg",
    "rga",
    "ugrep",
    "ouch",
    "pistol",
    "bat",
    "viu",
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
    "cpz",
    "rmz",
]

# Terminal & Shell Enhancements - Terminal multiplexers, shell history, and prompts
PACKAGES_TERMINAL_SHELL = [
    "zellij",
    "mprocs",
    "mcfly",
    "starship",
    "gotty",
    "ttyd",
    "rclone",
]





PACKAGE_GROUPS: TypeAlias = Literal[
    "ESSENTIAL",
    "DEV",
    "AGENTS",
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



# Main ESSENTIAL package list - combines all subgroups
ESSENTIAL = [
    *PACKAGES_CODE_ANALYSIS,
    *PACKAGES_SYSTEM_MONITORS,
    *PACKAGES_TERMINAL_SHELL,
    *PACKAGES_FILE,
]
DEV = [
    *PACKAGES_TERMINAL_EMULATORS,
    *PACKAGES_BROWSERS,
    *PACKAGES_CODE_EDITORS,
    *PACKAGES_DATABASE,
    *PACKAGES_MEDIA,
    *PACKAGES_FILE_SHARING,
    *PACKAGES_DEV_UTILS,
    *PACKAGES_CODE_ANALYSIS,
    *PACKAGES_PRODUCTIVITY,
    *PACKAGES_MISC_DEV,
]

PACKAGE_GROUP2NAMES: dict[PACKAGE_GROUPS, list[str]] = {
    "ESSENTIAL": ESSENTIAL,
    "DEV": DEV,
    "AGENTS": AGENTS,
    "TERMINAL_EMULATORS": PACKAGES_TERMINAL_EMULATORS,
    "BROWSERS": PACKAGES_BROWSERS,
    "CODE_EDITORS": PACKAGES_CODE_EDITORS,
    "DATABASE": PACKAGES_DATABASE,
    "MEDIA": PACKAGES_MEDIA,
    "FILE_SHARING": PACKAGES_FILE_SHARING,
    "DEV_UTILS": PACKAGES_DEV_UTILS,
    "CODE_ANALYSIS": PACKAGES_CODE_ANALYSIS,
    "PRODUCTIVITY": PACKAGES_PRODUCTIVITY,
    "MISC_DEV": PACKAGES_MISC_DEV,
    "SYSTEM_MONITORS": PACKAGES_SYSTEM_MONITORS,
    "SEARCH": PACKAGES_FILE,
    "TERMINAL_SHELL": PACKAGES_TERMINAL_SHELL,
}

_ = Union, Literal
