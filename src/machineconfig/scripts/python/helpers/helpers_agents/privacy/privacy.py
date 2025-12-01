"""

create 18 tasks one per cli
in each one, you do comprehensive search on internet on how to set up the cli/extension or whatever so we get max privacy and security (nothing shared everything is declined and is on the safe side)
this is a moving space, everyday, there are new versions, new configs, new settings, new policies, new rules, new terms of service, new eula, new privacy policies etc etc
so please search for latest and don't be complacent with the work done so far.

do it one by one, don't research and implement next before finishing the task before it.

I provided gemini cli solution as a reference (feel free to make it more flexible if you need mroe room to implement something more complex than what I did, its just a guide)
remember that other cli's have different names and configs and locations etc, read official docs

in the following cli how to set it for maximal prviacy *turn off any telemetry, reject any use of data, etc etc, please think of everything and read all theird docs and fine print
    "aider",
    "aichat",  # rust cli
    "copilot",  # cli from github copilot extension
    "gemini",  # gemini cli 
    "crush",  # cli from charm team
    "mods",  # cli from same people as crush (not agent) @ https://github.com/charmbracelet/mods
    "opencode-ai",
    "chatgpt",
    "q",  # from aws
    "qwen-code",  # fork of gemini cli
    "cursor-cli",
    "droid",
    "kilocode",
    "cline",  # cli from cline ai extension
    "auggie",
    "codex",  # from openai

"""

from typing import Optional


def apply_max_privacy_and_security_rules_and_configs(overwrite: bool, repo_root: Optional[str]) -> None:
    from machineconfig.utils.source_of_truth import LIBRARY_ROOT
    root = LIBRARY_ROOT / "scripts/python/helpers_agents/privacy/configs"
    from pathlib import Path

    # Gemini privacy settings
    gemini_settings_source = root.joinpath("gemini/settings.json")
    gemini_settings_target_global = Path.home().joinpath(".gemini/settings.json")
    if not gemini_settings_target_global.exists() or overwrite:
        gemini_settings_target_global.parent.mkdir(parents=True, exist_ok=True)
        gemini_settings_target_global.write_text(gemini_settings_source.read_text())
    if repo_root:
        gemini_settings_target_repo = Path(repo_root).joinpath(".gemini/settings.json")
        if not gemini_settings_target_repo.exists() or overwrite:
            gemini_settings_target_repo.parent.mkdir(parents=True, exist_ok=True)
            gemini_settings_target_repo.write_text(gemini_settings_source.read_text())

    # Aider privacy settings
    aider_settings_source = root.joinpath("aider/.aider.conf.yml")
    aider_settings_target_global = Path.home().joinpath(".aider.conf.yml")
    if not aider_settings_target_global.exists() or overwrite:
        aider_settings_target_global.parent.mkdir(parents=True, exist_ok=True)
        aider_settings_target_global.write_text(aider_settings_source.read_text())

    if repo_root:
        aider_settings_target_repo = Path(repo_root).joinpath(".aider.conf.yml")
        if not aider_settings_target_repo.exists() or overwrite:
            aider_settings_target_repo.parent.mkdir(parents=True, exist_ok=True)
            aider_settings_target_repo.write_text(aider_settings_source.read_text())

    # Aichat privacy settings
    aichat_settings_source = root.joinpath("aichat/config.yaml")
    aichat_settings_target_global = Path.home().joinpath(".config/aichat/config.yaml")
    if not aichat_settings_target_global.exists() or overwrite:
        aichat_settings_target_global.parent.mkdir(parents=True, exist_ok=True)
        aichat_settings_target_global.write_text(aichat_settings_source.read_text())

    if repo_root:
        aichat_settings_target_repo = Path(repo_root).joinpath(".config/aichat/config.yaml")
        if not aichat_settings_target_repo.exists() or overwrite:
            aichat_settings_target_repo.parent.mkdir(parents=True, exist_ok=True)
            aichat_settings_target_repo.write_text(aichat_settings_source.read_text())

    # Copilot privacy settings
    copilot_settings_source = root.joinpath("copilot/config.yml")
    copilot_settings_target_global = Path.home().joinpath(".config/gh-copilot/config.yml")
    if not copilot_settings_target_global.exists() or overwrite:
        copilot_settings_target_global.parent.mkdir(parents=True, exist_ok=True)
        copilot_settings_target_global.write_text(copilot_settings_source.read_text())

    if repo_root:
        copilot_settings_target_repo = Path(repo_root).joinpath(".config/gh-copilot/config.yml")
        if not copilot_settings_target_repo.exists() or overwrite:
            copilot_settings_target_repo.parent.mkdir(parents=True, exist_ok=True)
            copilot_settings_target_repo.write_text(copilot_settings_source.read_text())

    # Crush privacy settings
    crush_settings_source = root.joinpath("crush/crush.json")
    crush_settings_target_global = Path.home().joinpath(".config/crush/crush.json")
    if not crush_settings_target_global.exists() or overwrite:
        crush_settings_target_global.parent.mkdir(parents=True, exist_ok=True)
        crush_settings_target_global.write_text(crush_settings_source.read_text())

    if repo_root:
        crush_settings_target_repo = Path(repo_root).joinpath(".crush.json")
        if not crush_settings_target_repo.exists() or overwrite:
            crush_settings_target_repo.parent.mkdir(parents=True, exist_ok=True)
            crush_settings_target_repo.write_text(crush_settings_source.read_text())

    # next, cursh cli


if __name__ == "__main__":
    pass
