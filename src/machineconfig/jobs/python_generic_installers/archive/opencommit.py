
# from machineconfig.utils.utils import write_shell_script
# import crocodile.toolbox as tb
from typing import Optional

__doc__ = """OpenCommit is a tool for writing better commit messages using GPT-3"""
repo_url = "https://github.com/di-sukharev/opencommit"


def main(version: Optional[str] = None):
    _ = version
    # token = input("Enter your OpenAI API key: ")
    token = 1
    program = f"""
# as per: {repo_url}
npm install -g opencommit
cd ~
# echo "OPENAI_API_KEY={token}" > .opencommit
"""
    # tb.Terminal().run(program, shell="powershell").print()
    return program


if __name__ == '__main__':
    pass
