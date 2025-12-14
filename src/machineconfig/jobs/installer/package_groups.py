
GUI = [
    "brave",
    "code",
    "git",
    # "wezterm",  # needs admin
]

# AI/LLM Tools - AI-powered coding and chat assistants
AGENTS = [
    "aider",
    "aichat",
    "copilot",
    "gemini",
    "crush",
    "opencode-ai",
    "chatgpt",
    "mods",
    "q",
    "qwen-code",
    "cursor-cli",
    "droid",
    "kilocode",
    "cline",
    "auggie",
    # "codex",
    # "gorilla",
    # "ollama",
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
    "sqlite3",
    "redis",
    "redis-cli",
    "postgresql-client",
    "duckdb",
    "DBeaver",
    "rainfrog",

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
    "nano",
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


TERMINAL_EYE_CANDY = [
    "lolcatjs",
    "figlet-cli",
    "boxes",
    "cowsay",
    # "transmission",
    # "bytehound",
    # "xcrawl3r",
    # "obsidian",
    # "istio",
    # "cointop",
# sudo nala install cowsay -y || true
# sudo nala install lolcat -y || true
# sudo nala install boxes -y || true
# sudo nala install figlet -y || true
# sudo nala install fortune -y || true
# sudo nala install toilet -y || true
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
    "fd",
    "fzf",
    "tv",
    "broot",
    "rg",
    "rga",
    "ugrep",
    "ouch",
    "pistol",
    "bat",
    "viu",
    # "xplr",
    # "joshuto",
    # "lf",
    # "nnn",
    "yazi",
    "tere",
    # "exa",
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
    # "mcfly",
    "atuin",
    "starship",
    "gotty",
    "ttyd",
    "rclone",
    "cb"
]



PACKAGE_GROUP2NAMES: dict[str, list[str]] = {
    "sysabc": ["sysabc"],
    "termabc": [*PACKAGES_CODE_ANALYSIS, *PACKAGES_SYSTEM_MONITORS, *PACKAGES_TERMINAL_SHELL, *PACKAGES_FILE,],
    "gui": GUI,
    "dev": [*PACKAGES_TERMINAL_EMULATORS, *PACKAGES_BROWSERS, *PACKAGES_CODE_EDITORS, *PACKAGES_DATABASE, *PACKAGES_MEDIA, *PACKAGES_FILE_SHARING, *PACKAGES_DEV_UTILS, *PACKAGES_CODE_ANALYSIS, *PACKAGES_PRODUCTIVITY, *TERMINAL_EYE_CANDY,],
    "dev-utils": PACKAGES_DEV_UTILS,
    "term-eye-candy": TERMINAL_EYE_CANDY,
    "agents": AGENTS,
    "terminal-emulator": PACKAGES_TERMINAL_EMULATORS,
    "shell": PACKAGES_TERMINAL_SHELL,
    "browsers": PACKAGES_BROWSERS,
    "code-editors": PACKAGES_CODE_EDITORS,
    "code-analysis": PACKAGES_CODE_ANALYSIS,
    "db": PACKAGES_DATABASE,
    "media": PACKAGES_MEDIA,
    "file-sharing": PACKAGES_FILE_SHARING,
    "productivity": PACKAGES_PRODUCTIVITY,
    "sys-monitor": PACKAGES_SYSTEM_MONITORS,
    "search": PACKAGES_FILE,
}
