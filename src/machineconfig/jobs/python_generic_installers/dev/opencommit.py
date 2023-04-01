
# from machineconfig.utils.utils import write_shell_script
import crocodile.toolbox as tb


def main(version=None):
    _ = version
    token = input("Enter your OpenAI API key: ")
    program = f"""
    # as per: https://github.com/di-sukharev/opencommit
    npm install -g opencommit
    cd ~
    echo "OPENAI_API_KEY={token}" > .opencommit
    """
    tb.Terminal().run(program, shell="powershell")


if __name__ == '__main__':
    pass
