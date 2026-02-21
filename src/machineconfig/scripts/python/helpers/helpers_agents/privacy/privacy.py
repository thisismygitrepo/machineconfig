from machineconfig.scripts.python.helpers.helpers_agents.privacy.configs.auggie.auggie_privacy import secure_auggie_config
from machineconfig.scripts.python.helpers.helpers_agents.privacy.configs.chatgpt.chatgpt_privacy import secure_chatgpt_cli
from machineconfig.scripts.python.helpers.helpers_agents.privacy.configs.cline.cline_privacy import secure_cline_config
from machineconfig.scripts.python.helpers.helpers_agents.privacy.configs.codex.codex_privacy import secure_codex_configs
from machineconfig.scripts.python.helpers.helpers_agents.privacy.configs.common.privacy_orchestrator import apply_max_privacy_and_security_rules_and_configs
from machineconfig.scripts.python.helpers.helpers_agents.privacy.configs.cursor.cursor_privacy import secure_cursor_cli
from machineconfig.scripts.python.helpers.helpers_agents.privacy.configs.droid.droid_privacy import secure_droid_cli
from machineconfig.scripts.python.helpers.helpers_agents.privacy.configs.kilocode.kilocode_privacy import secure_kilocode_config
from machineconfig.scripts.python.helpers.helpers_agents.privacy.configs.mods.mods_privacy import secure_mods_config
from machineconfig.scripts.python.helpers.helpers_agents.privacy.configs.q.q_privacy import secure_q_cli
from machineconfig.scripts.python.helpers.helpers_agents.privacy.configs.qwen.qwen_privacy import secure_qwen_config

__all__ = [
    "apply_max_privacy_and_security_rules_and_configs",
    "secure_mods_config",
    "secure_chatgpt_cli",
    "secure_q_cli",
    "secure_qwen_config",
    "secure_cursor_cli",
    "secure_droid_cli",
    "secure_kilocode_config",
    "secure_cline_config",
    "secure_auggie_config",
    "secure_codex_configs",
]

if __name__ == "__main__":
    apply_max_privacy_and_security_rules_and_configs(overwrite=True, repo_root=None)
