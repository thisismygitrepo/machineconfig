"""ID"""

# from platform import system
from machineconfig.utils.path_extended import PathExtended
from machineconfig.utils.options import choose_from_options
from rich.panel import Panel
from rich.text import Text

BOX_WIDTH = 150  # width for box drawing


def main() -> None:
    title = "🔑 SSH IDENTITY MANAGEMENT"
    print(Panel(Text(title, justify="center"), expand=False))
    print(Panel("🔍 Searching for existing SSH keys...", expand=False))
    private_keys = [x.with_name(x.stem) for x in PathExtended.home().joinpath(".ssh").search("*.pub")]
    private_keys = [x for x in private_keys if x.exists()]
    if private_keys:
        print(Panel(f"✅ Found {len(private_keys)} SSH private key(s)", expand=False))
    else:
        print(Panel("⚠️  No SSH private keys found", expand=False))

    choice = choose_from_options(msg="Path to private key to be used when ssh'ing: ", options=[str(x) for x in private_keys] + ["I have the path to the key file", "I want to paste the key itself"], multi=False)

    if choice == "I have the path to the key file":
        print(Panel("📄 Please enter the path to your private key file", expand=False))
        path_to_key = PathExtended(input("📋 Input path here: ")).expanduser().absolute()
        print(Panel(f"📂 Using key from custom path: {path_to_key}", expand=False))

    elif choice == "I want to paste the key itself":
        print(Panel("📋 Please provide a filename and paste the private key content", expand=False))
        key_filename = input("📝 File name (default: my_pasted_key): ") or "my_pasted_key"
        path_to_key = PathExtended.home().joinpath(f".ssh/{key_filename}")
        path_to_key.parent.mkdir(parents=True, exist_ok=True)
        path_to_key.write_text(input("🔑 Paste the private key here: "), encoding="utf-8")
        print(Panel(f"💾 Key saved to: {path_to_key}", expand=False))

    else:
        path_to_key = PathExtended(choice)
        print(Panel(f"🔑 Using selected key: {path_to_key.name}", expand=False))

    txt = f"IdentityFile {path_to_key.collapseuser().as_posix()}"  # adds this id for all connections, no host specified.
    config_path = PathExtended.home().joinpath(".ssh/config")

    print(Panel("📝 Updating SSH configuration...", expand=False))

    # Inline the previous modify_text behavior (now deprecated):
    # - If file doesn't exist, seed content with txt_search
    # - Otherwise, replace a matching line or append if not found
    if config_path.exists():
        current = config_path.read_text(encoding="utf-8")
        print(Panel("✏️  Updated existing SSH config file", expand=False))
    else:
        current = txt
        print(Panel("📄 Created new SSH config file", expand=False))
    lines = current.split("\n")
    found = False
    for i, line in enumerate(lines):
        if txt in line:
            lines[i] = txt
            found = True
    if not found:
        lines.insert(0, txt)
    new_content = "\n".join(lines)
    config_path.write_text(new_content, encoding="utf-8")

    panel_complete = Panel(Text("✅ SSH IDENTITY CONFIGURATION COMPLETE\nIdentity added to SSH config file\nConsider reloading the SSH config to apply changes", justify="center"), expand=False, border_style="green")
    program = f"echo '{panel_complete}'"

    success_message = f"🎉 CONFIGURATION SUCCESSFUL\nIdentity added: {path_to_key.name}\nConfig file: {config_path}"
    print(Panel(Text(success_message, justify="center"), expand=False, border_style="green"))

    import subprocess

    # run program
    subprocess.run(program, shell=True, check=True, text=True)
    print(Panel("🔐 Identity added to SSH agent", expand=False, border_style="green"))
    return None


if __name__ == "__main__":
    pass
