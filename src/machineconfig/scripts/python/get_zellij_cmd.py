from pathlib import Path


def get_zellij_cmd(wd1: Path, wd2: Path) -> str:
    _ = wd1, wd2
    lines = [
        """ zellij action new-tab --name gitdiff""",
        """zellij action new-pane --direction down --name local --cwd ./data """,
        """zellij action write-chars "cd '{wd1}'; git status" """,
        """zellij action move-focus up; zellij action close-pane """,
        """zellij action new-pane --direction down --name remote --cwd code """,
        """zellij action write-chars "cd '{wd2}' """,
        """git status" """,
    ]
    return "; ".join(lines)
