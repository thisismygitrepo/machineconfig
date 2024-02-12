
"""ngrok
"""

import platform


def main():
    if platform.system() == "Windows":
        program = "winget install ngrok.ngrok"
    elif platform.system() == "Linux":
        # as per https://ngrok.com/docs/getting-started/?os=linux
        program = """

curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | \
sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && \
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | \
sudo tee /etc/apt/sources.list.d/ngrok.list && \
sudo apt update && sudo apt install ngrok
"""
    else:
        raise NotImplementedError("unsupported platform")
    from crocodile.meta import Terminal
    Terminal().run(program, shell="powershell")
    return program


if __name__ == "__main__":
    main()
