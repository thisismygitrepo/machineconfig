"""
Command tree widget for displaying command hierarchy.
"""

from textual.widgets import Tree
from machineconfig.scripts.python.helpers_navigator.data_models import CommandInfo


class CommandTree(Tree[CommandInfo]):
    """Tree widget for displaying command hierarchy."""

    def on_mount(self) -> None:
        """Build the command tree when mounted."""
        self.show_root = False
        self.guide_depth = 2
        self._build_command_tree()

    def _build_command_tree(self) -> None:
        """Build the hierarchical command structure."""

        # Main entry points
        devops_node = self.root.add("🛠️  devops - DevOps operations", data=CommandInfo(
            name="devops",
            description="DevOps operations",
            command="devops",
            is_group=True,
            module_path="machineconfig.scripts.python.devops"
        ))

        # devops subcommands
        devops_node.add("📦 install - Install essential packages", data=CommandInfo(
            name="install",
            description="Install essential packages",
            command="devops install",
            parent="devops",
            help_text="devops install --which <packages> --group <group> --interactive"
        ))

        repos_node = devops_node.add("📁 repos - Manage git repositories", data=CommandInfo(
            name="repos",
            description="Manage git repositories",
            command="devops repos",
            parent="devops",
            is_group=True,
            module_path="machineconfig.scripts.python.devops_helpers.cli_repos"
        ))

        # repos subcommands
        repos_node.add("🚀 push - Push changes across repositories", data=CommandInfo(
            name="push",
            description="Push changes across repositories",
            command="devops repos push",
            parent="repos",
            help_text="devops repos push --directory <dir> --recursive --no-sync"
        ))

        repos_node.add("⬇️ pull - Pull changes across repositories", data=CommandInfo(
            name="pull",
            description="Pull changes across repositories",
            command="devops repos pull",
            parent="repos",
            help_text="devops repos pull --directory <dir> --recursive --no-sync"
        ))

        repos_node.add("💾 commit - Commit changes across repositories", data=CommandInfo(
            name="commit",
            description="Commit changes across repositories",
            command="devops repos commit",
            parent="repos",
            help_text="devops repos commit --directory <dir> --recursive --no-sync"
        ))

        repos_node.add("🔄 sync - Sync changes across repositories", data=CommandInfo(
            name="sync",
            description="Pull, commit, and push changes across repositories",
            command="devops repos sync",
            parent="repos",
            help_text="devops repos sync --directory <dir> --recursive --no-sync"
        ))

        mirror_node = repos_node.add("🔄 mirror - Manage repository specifications", data=CommandInfo(
            name="mirror",
            description="Manage repository specifications and syncing",
            command="devops repos mirror",
            parent="repos",
            is_group=True
        ))

        mirror_node.add("📝 capture - Record repositories into repos.json", data=CommandInfo(
            name="capture",
            description="Record repositories into a repos.json specification",
            command="devops repos mirror capture",
            parent="mirror",
            help_text="devops repos mirror capture --directory <dir> --cloud <cloud>"
        ))

        mirror_node.add("📥 clone - Clone repositories from repos.json", data=CommandInfo(
            name="clone",
            description="Clone repositories described by repos.json",
            command="devops repos mirror clone",
            parent="mirror",
            help_text="devops repos mirror clone --directory <dir> --cloud <cloud>"
        ))

        mirror_node.add("🔀 checkout-to-commit - Check out specific commits", data=CommandInfo(
            name="checkout-to-commit",
            description="Check out specific commits listed in specification",
            command="devops repos mirror checkout-to-commit",
            parent="mirror",
            help_text="devops repos mirror checkout-to-commit --directory <dir> --cloud <cloud>"
        ))

        mirror_node.add("🔀 checkout-to-branch - Check out to main branch", data=CommandInfo(
            name="checkout-to-branch",
            description="Check out to the main branch defined in specification",
            command="devops repos mirror checkout-to-branch",
            parent="mirror",
            help_text="devops repos mirror checkout-to-branch --directory <dir> --cloud <cloud>"
        ))

        repos_node.add("🔍 analyze - Analyze repositories", data=CommandInfo(
            name="analyze",
            description="Analyze repositories in directory",
            command="devops repos analyze",
            parent="repos",
            help_text="devops repos analyze --directory <dir>"
        ))

        repos_node.add("🔐 secure - Securely sync git repository", data=CommandInfo(
            name="secure",
            description="Securely sync git repository to/from cloud with encryption",
            command="devops repos secure",
            parent="repos",
            help_text="devops repos secure <path> --cloud <cloud> --encrypt --decrypt"
        ))

        repos_node.add("🎬 viz - Visualize repository activity", data=CommandInfo(
            name="viz",
            description="Visualize repository activity using Gource",
            command="devops repos viz",
            parent="repos",
            help_text="devops repos viz --repo <path> --output <file> --resolution <res> --seconds-per-day <spd>"
        ))

        repos_node.add("🧹 cleanup - Clean repository directories", data=CommandInfo(
            name="cleanup",
            description="Clean repository directories from cache files",
            command="devops repos cleanup",
            parent="repos",
            help_text="devops repos cleanup --repo <path> --recursive"
        ))

        # config subcommands
        config_node = devops_node.add("⚙️  config - Configuration management", data=CommandInfo(
            name="config",
            description="Configuration subcommands",
            command="devops config",
            parent="devops",
            is_group=True
        ))

        config_node.add("🔗 private - Manage private configuration files", data=CommandInfo(
            name="private",
            description="Manage private configuration files",
            command="devops config private",
            parent="config",
            help_text="devops config private --method <symlink|copy> --on-conflict <action> --which <items> --interactive"
        ))

        config_node.add("🔗 public - Manage public configuration files", data=CommandInfo(
            name="public",
            description="Manage public configuration files",
            command="devops config public",
            parent="config",
            help_text="devops config public --method <symlink|copy> --on-conflict <action> --which <items> --interactive"
        ))

        config_node.add("🔗 dotfile - Manage dotfiles", data=CommandInfo(
            name="dotfile",
            description="Manage dotfiles",
            command="devops config dotfile",
            parent="config",
            help_text="devops config dotfile <file> --overwrite --dest <destination>"
        ))

        config_node.add("🔗 shell - Configure shell profile", data=CommandInfo(
            name="shell",
            description="Configure your shell profile",
            command="devops config shell",
            parent="config",
            help_text="devops config shell --which <default|nushell>"
        ))

        config_node.add("🔗 starship-theme - Select starship theme", data=CommandInfo(
            name="starship-theme",
            description="Select starship prompt theme",
            command="devops config starship-theme",
            parent="config",
            help_text="devops config starship-theme"
        ))

        config_node.add("🔗 pwsh-theme - Configure PowerShell theme", data=CommandInfo(
            name="pwsh-theme",
            description="Select powershell prompt theme",
            command="devops config pwsh-theme",
            parent="config",
            help_text="devops config pwsh-theme"
        ))

        config_node.add("🔗 copy-assets - Copy asset files", data=CommandInfo(
            name="copy-assets",
            description="Copy asset files from library to machine",
            command="devops config copy-assets",
            parent="config",
            help_text="devops config copy-assets <scripts|settings|both>"
        ))

        # data subcommands
        data_node = devops_node.add("💾 data - Data operations", data=CommandInfo(
            name="data",
            description="Data subcommands",
            command="devops data",
            parent="devops",
            is_group=True
        ))

        data_node.add("💾 backup - Backup data", data=CommandInfo(
            name="backup",
            description="Backup data",
            command="devops data backup",
            parent="data",
            help_text="devops data backup"
        ))

        data_node.add("📥 retrieve - Retrieve data", data=CommandInfo(
            name="retrieve",
            description="Retrieve data from backup",
            command="devops data retrieve",
            parent="data",
            help_text="devops data retrieve"
        ))

        # network subcommands
        network_node = devops_node.add("🔐 network - Network operations", data=CommandInfo(
            name="network",
            description="Network subcommands",
            command="devops network",
            parent="devops",
            is_group=True
        ))

        network_node.add("📡 share-terminal - Share terminal via web", data=CommandInfo(
            name="share-terminal",
            description="Share terminal via web browser",
            command="devops network share-terminal",
            parent="network",
            help_text="devops network share-terminal"
        ))

        network_node.add("🌐 share-server - Start local/global server", data=CommandInfo(
            name="share-server",
            description="Start local/global server to share files/folders via web browser",
            command="devops network share-server",
            parent="network",
            help_text="devops network share-server"
        ))

        network_node.add("📡 install-ssh-server - Install SSH server", data=CommandInfo(
            name="install-ssh-server",
            description="Install SSH server",
            command="devops network install-ssh-server",
            parent="network",
            help_text="devops network install-ssh-server"
        ))

        network_node.add("🔑 add-ssh-key - Add SSH public key", data=CommandInfo(
            name="add-ssh-key",
            description="Add SSH public key to this machine",
            command="devops network add-ssh-key",
            parent="network",
            help_text="devops network add-ssh-key --path <file> --choose --value --github <username>"
        ))

        network_node.add("🗝️ add-ssh-identity - Add SSH identity", data=CommandInfo(
            name="add-ssh-identity",
            description="Add SSH identity (private key) to this machine",
            command="devops network add-ssh-identity",
            parent="network",
            help_text="devops network add-ssh-identity"
        ))

        network_node.add("📌 show-address - Show computer addresses", data=CommandInfo(
            name="show-address",
            description="Show this computer addresses on network",
            command="devops network show-address",
            parent="network",
            help_text="devops network show-address"
        ))

        network_node.add("🐛 debug-ssh - Debug SSH connection", data=CommandInfo(
            name="debug-ssh",
            description="Debug SSH connection",
            command="devops network debug-ssh",
            parent="network",
            help_text="devops network debug-ssh"
        ))

        # self subcommands
        self_node = devops_node.add("🔄 self - SELF operations", data=CommandInfo(
            name="self",
            description="SELF operations subcommands",
            command="devops self",
            parent="devops",
            is_group=True
        ))

        self_node.add("🔄 update - Update essential repos", data=CommandInfo(
            name="update",
            description="Update essential repos",
            command="devops self update",
            parent="self",
            help_text="devops self update"
        ))

        self_node.add("🤖 interactive - Interactive configuration", data=CommandInfo(
            name="interactive",
            description="Interactive configuration of machine",
            command="devops self interactive",
            parent="self",
            help_text="devops self interactive"
        ))

        self_node.add("📊 status - Machine status", data=CommandInfo(
            name="status",
            description="Status of machine, shell profile, apps, symlinks, dotfiles, etc.",
            command="devops self status",
            parent="self",
            help_text="devops self status"
        ))

        self_node.add("📋 clone - Clone machineconfig", data=CommandInfo(
            name="clone",
            description="Clone machineconfig locally and incorporate to shell profile",
            command="devops self clone",
            parent="self",
            help_text="devops self clone"
        ))

        self_node.add("📚 navigate - Navigate command structure", data=CommandInfo(
            name="navigate",
            description="Navigate command structure with TUI",
            command="devops self navigate",
            parent="self",
            help_text="devops self navigate"
        ))

        self_node.add("📚 readme - Render README markdown", data=CommandInfo(
            name="readme",
            description="Render readme markdown in terminal",
            command="devops self readme",
            parent="self",
            help_text="devops self readme"
        ))

        self_node.add("🐍 python - Run Python command/file", data=CommandInfo(
            name="python",
            description="Run python command/file in the machineconfig environment",
            command="devops self python",
            parent="self",
            help_text="devops self python <path> --command"
        ))

        # fire command - now a typer sub-app
        fire_node = self.root.add("🔥 fire - Fire jobs execution", data=CommandInfo(
            name="fire",
            description="Fire and manage jobs",
            command="fire",
            is_group=True,
            module_path="machineconfig.scripts.python.fire_jobs"
        ))

        fire_node.add("🔥 fire - Execute Python/Shell scripts", data=CommandInfo(
            name="fire",
            description="Execute Python scripts, shell scripts, or PowerShell scripts with Fire",
            command="fire",
            parent="fire",
            help_text="fire <path> [function] --ve <env> --cmd --interactive --debug --choose_function --loop --jupyter --submit_to_cloud --remote --module --streamlit --environment <env> --holdDirectory --PathExport --git_pull --optimized --zellij_tab <name> --watch"
        ))

        # agents command
        agents_node = self.root.add("🤖 agents - AI Agents management", data=CommandInfo(
            name="agents",
            description="AI Agents management subcommands",
            command="agents",
            is_group=True,
            module_path="machineconfig.scripts.python.agents"
        ))

        agents_node.add("✨ create - Create AI agent", data=CommandInfo(
            name="create",
            description="Create a new AI agent",
            command="agents create",
            parent="agents",
            help_text="agents create --context-path <file> --keyword-search <term> --filename-pattern <pattern> --agent <type> --machine <target> --model <model> --provider <provider> --prompt <text> --prompt-path <file> --job-name <name> --tasks-per-prompt <num> --separate-prompt-from-context --output-path <file> --agents-dir <dir>"
        ))

        agents_node.add("📦 collect - Collect agent data", data=CommandInfo(
            name="collect",
            description="Collect agent data",
            command="agents collect",
            parent="agents",
            help_text="agents collect --agent-dir <dir> --output-path <file> --separator <sep>"
        ))

        agents_node.add("📝 make-template - Create agent template", data=CommandInfo(
            name="make-template",
            description="Create a template for fire agents",
            command="agents make-template",
            parent="agents",
            help_text="agents make-template"
        ))

        agents_node.add("⚙️  make-config - Initialize AI configurations", data=CommandInfo(
            name="make-config",
            description="Initialize AI configurations in the current repository",
            command="agents make-config",
            parent="agents",
            help_text="agents make-config"
        ))

        agents_node.add("📝 make-todo - Generate todo markdown", data=CommandInfo(
            name="make-todo",
            description="Generate a markdown file listing all Python files in the repo",
            command="agents make-todo",
            parent="agents",
            help_text="agents make-todo"
        ))

        agents_node.add("🔗 make-symlinks - Create repo symlinks", data=CommandInfo(
            name="make-symlinks",
            description="Create symlinks to the current repo in ~/code_copies/",
            command="agents make-symlinks",
            parent="agents",
            help_text="agents make-symlinks"
        ))

        # sessions command
        sessions_node = self.root.add("🖥️  sessions - Session layouts management", data=CommandInfo(
            name="sessions",
            description="Layouts management subcommands",
            command="sessions",
            is_group=True,
            module_path="machineconfig.scripts.python.sessions"
        ))

        sessions_node.add("✨ create-from-function - Create layout from function", data=CommandInfo(
            name="create-from-function",
            description="Create layout from function",
            command="sessions create-from-function",
            parent="sessions",
            help_text="sessions create-from-function"
        ))

        sessions_node.add("▶️  run - Run session layout", data=CommandInfo(
            name="run",
            description="Run session layout",
            command="sessions run",
            parent="sessions",
            help_text="sessions run --layout-path <file> --max-tabs <num> --max-layouts <num> --sleep-inbetween <sec> --monitor --parallel --kill-upon-completion --choose <names> --choose-interactively"
        ))

        sessions_node.add("⚖️  balance-load - Balance load", data=CommandInfo(
            name="balance-load",
            description="Balance load across sessions",
            command="sessions balance-load",
            parent="sessions",
            help_text="sessions balance-load --layout-path <file> --max-thresh <num> --thresh-type <number|weight> --breaking-method <moreLayouts|combineTabs> --output-path <file>"
        ))

        sessions_node.add("💀 kill-process - Kill processes", data=CommandInfo(
            name="kill-process",
            description="Choose a process to kill interactively",
            command="sessions kill-process",
            parent="sessions",
            help_text="sessions kill-process"
        ))

        # cloud command
        cloud_node = self.root.add("☁️  cloud - Cloud storage operations", data=CommandInfo(
            name="cloud",
            description="Cloud storage operations",
            command="cloud",
            is_group=True,
            module_path="machineconfig.scripts.python.cloud"
        ))

        cloud_node.add("🔄 sync - Synchronize with cloud", data=CommandInfo(
            name="sync",
            description="Synchronize files/folders between local and cloud storage",
            command="cloud sync",
            parent="cloud",
            help_text="cloud sync <source> <target> --cloud <provider> --recursive --exclude <patterns>"
        ))

        cloud_node.add("📤 copy - Copy to/from cloud", data=CommandInfo(
            name="copy",
            description="Copy files/folders to/from cloud storage",
            command="cloud copy",
            parent="cloud",
            help_text="cloud copy <source> <target> --cloud <provider> --recursive --exclude <patterns>"
        ))

        cloud_node.add("🔗 mount - Mount cloud storage", data=CommandInfo(
            name="mount",
            description="Mount cloud storage as local drive",
            command="cloud mount",
            parent="cloud",
            help_text="cloud mount <remote> <mount_point> --cloud <provider> --daemon --allow-other"
        ))

        # croshell command
        self.root.add("🔄 croshell - Cross-shell command execution", data=CommandInfo(
            name="croshell",
            description="Cross-shell command execution",
            command="croshell",
            is_group=False,
            module_path="machineconfig.scripts.python.croshell",
            help_text="croshell --python --fzf --ve <env> --profile <profile> --read <file> --jupyter --streamlit --visidata"
        ))

        # ftpx command
        self.root.add("📡 ftpx - File transfer utility", data=CommandInfo(
            name="ftpx",
            description="File transfer utility through SSH",
            command="ftpx",
            is_group=False,
            module_path="machineconfig.scripts.python.ftpx",
            help_text="ftpx <source> <target> --recursive --zipFirst --cloud"
        ))

        # utils command
        utils_node = self.root.add("🛠️ utils - Utility commands", data=CommandInfo(
            name="utils",
            description="Utility commands",
            command="utils",
            is_group=True,
            module_path="machineconfig.scripts.python.utils"
        ))

        utils_node.add("💀 kill-process - Kill processes", data=CommandInfo(
            name="kill-process",
            description="Choose a process to kill interactively",
            command="utils kill-process",
            parent="utils",
            help_text="utils kill-process --interactive"
        ))

        utils_node.add("📚 path - Navigate PATH variable", data=CommandInfo(
            name="path",
            description="Navigate PATH variable with TUI",
            command="utils path",
            parent="utils",
            help_text="utils path"
        ))

        utils_node.add("⬆️ upgrade-packages - Upgrade dependencies", data=CommandInfo(
            name="upgrade-packages",
            description="Upgrade project dependencies",
            command="utils upgrade-packages",
            parent="utils",
            help_text="utils upgrade-packages"
        ))

        utils_node.add("⬇️ download - Download file", data=CommandInfo(
            name="download",
            description="Download a file from a URL and optionally decompress it",
            command="utils download",
            parent="utils",
            help_text="utils download <url> --destination <path> --decompress"
        ))

        utils_node.add("🖥️ get-machine-specs - Get machine specifications", data=CommandInfo(
            name="get-machine-specs",
            description="Get machine specifications",
            command="utils get-machine-specs",
            parent="utils",
            help_text="utils get-machine-specs"
        ))

        utils_node.add("🚀 init-project - Initialize project", data=CommandInfo(
            name="init-project",
            description="Initialize a project with a uv virtual environment and install dev packages",
            command="utils init-project",
            parent="utils",
            help_text="utils init-project"
        ))

        utils_node.add("✏️ edit - Open file in editor", data=CommandInfo(
            name="edit",
            description="Open a file in the default editor",
            command="utils edit",
            parent="utils",
            help_text="utils edit <file>"
        ))

        utils_node.add("📄 pdf-merge - Merge PDF files", data=CommandInfo(
            name="pdf-merge",
            description="Merge two PDF files into one",
            command="utils pdf-merge",
            parent="utils",
            help_text="utils pdf-merge <file1> <file2> --output <file>"
        ))

        utils_node.add("� pdf-compress - Compress PDF file", data=CommandInfo(
            name="pdf-compress",
            description="Compress a PDF file",
            command="utils pdf-compress",
            parent="utils",
            help_text="utils pdf-compress <file> --output <file>"
        ))