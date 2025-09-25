"""Notifications Module"""

# from crocodile.core import install_n_import
# from crocodile.file_management import P, Read
from pathlib import Path

# from crocodile.meta import RepeatUntilNoException
import smtplib
import imaplib

# from email import message
# from email import encoders
# from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Any, Union
from rich.console import Console
from rich.markdown import Markdown


def download_to_memory(path: Path, allow_redirects: bool = True, timeout: Optional[float] = None, params: Any = None) -> "Any":
    import requests

    return requests.get(
        path.as_posix().replace("https:/", "https://").replace("http:/", "http://"), allow_redirects=allow_redirects, timeout=timeout, params=params
    )  # Alternative: from urllib import request; request.urlopen(url).read().decode('utf-8').


def get_github_markdown_css() -> str:
    pp = r"https://raw.githubusercontent.com/sindresorhus/github-markdown-css/main/github-markdown-dark.css"
    return download_to_memory(Path(pp)).text


def md2html(body: str) -> str:
    """Convert markdown to HTML using Rich library."""
    # Use Rich's HTML export functionality to convert markdown to HTML
    console = Console(record=True, width=120)
    markdown_obj = Markdown(body)
    console.print(markdown_obj)
    html_output = console.export_html(inline_styles=True)

    # Try to load GitHub CSS style, fallback to basic style if not found
    gh_style_path = Path(__file__).parent.joinpath("gh_style.css")
    if gh_style_path.exists():
        gh_style = gh_style_path.read_text()
    else:
        # Fallback basic styling
        gh_style = """
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
        h1, h2, h3, h4, h5, h6 { color: #0366d6; }
        code { background-color: #f6f8fa; padding: 2px 4px; border-radius: 3px; }
        pre { background-color: #f6f8fa; padding: 16px; border-radius: 6px; overflow: auto; }
        """

    return f"""
<!DOCTYPE html>
<html>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
{gh_style}
    .markdown-body {{
        box-sizing: border-box;
        min-width: 200px;
        max-width: 1350px;
        margin: 0 auto;
        padding: 45px;
        line-height: 1.8;
    }}
    @media (max-width: 767px) {{.markdown-body {{padding: 15px;}}
    }}
</style>
<body>
<div class="markdown-body">
{html_output}
</div>
</body>
</html>"""


class Email:
    @staticmethod
    def get_source_of_truth():
        path = Path.home().joinpath("dotfiles/machineconfig/emails.ini")
        if not path.exists():
            raise FileNotFoundError(f"""File not found: {path}. It should be an ini file with this structure
[resend]
api_key = xxx

[config1]
email_add = a@b.com
password = 123
smtp_host = a@b.com
smtp_port = 465
imap_host = b@c.com
imap_port = 465
encryption = ssl

""")

        if not Path(path).exists() or Path(path).is_dir():
            raise FileNotFoundError(f"File not found or is a directory: {path}")
        import configparser

        res = configparser.ConfigParser()
        res.read(filenames=[str(path)], encoding=None)
        return res

    def __init__(self, config: dict[str, Any]):
        self.config = config
        from smtplib import SMTP_SSL, SMTP

        self.server: Union[SMTP_SSL, SMTP]
        if config["encryption"].lower() == "ssl":
            self.server = smtplib.SMTP_SSL(host=self.config["smtp_host"], port=self.config["smtp_port"])
        elif config["encryption"].lower() == "tls":
            self.server = smtplib.SMTP(host=self.config["smtp_host"], port=self.config["smtp_port"])
        self.server.login(self.config["email_add"], password=self.config["password"])

    def send_message(self, to: str, subject: str, body: str, txt_to_html: bool = True, attachments: Optional[list[Any]] = None):
        _ = attachments
        body += "\n\nThis is an automated email sent via crocodile.comms script."
        # msg = message.EmailMessage()
        msg = MIMEMultipart("alternative")
        msg["subject"] = subject
        msg["From"] = self.config["email_add"]
        msg["To"] = to
        # msg['Content-Type'] = "text/html"
        # msg.set_content(body)

        # <link rel="stylesheet" href="github-markdown.css">
        # <link type="text/css" rel="stylesheet" href="https://raw.githubusercontent.com/sindresorhus/github-markdown-css/main/github-markdown-dark.css" />

        if txt_to_html:
            body = md2html(body=body)
        msg.attach(MIMEText(body, "html"))
        # if attachments is None: attachments = []  # see: https://fedingo.com/how-to-send-html-mail-with-attachment-using-python/
        # for attachment in attachmenthrs: msg.attach(attachment.read_bytes(), filename=attachment.stem, maintype="image", subtype=attachment.suffix)
        # for attachment in attachments: msg.attach(attachment.read_bytes(), filename=attachment.stem, maintype="application", subtype="octet-stream")

        self.server.send_message(msg)

    @staticmethod
    def manage_folders(email_add: str, pwd: str):
        server = imaplib.IMAP4()
        server.starttls()
        server.login(email_add, password=pwd)

    def send_email(self, to_addrs: str, msg: str):
        return self.server.sendmail(from_addr=self.config["email_add"], to_addrs=to_addrs, msg=msg)

    def close(self):
        self.server.quit()  # Closing is vital as many servers do not allow mutiple connections.

    @staticmethod
    def send_and_close(config_name: Optional[str], to: str, subject: str, body: str) -> Any:
        """If config_name is None, it sends from a generic email address."""
        if config_name is None:
            raise NotImplementedError(
                "Sending email without a config_name is not implemented. You need to create an emails.ini file in ~/dotfiles/machineconfig/ with your email configuration. See the docstring of the get_source_of_truth method for more information."
            )
            # config = Email.get_source_of_truth()
            # try:
            #     api_key = config['resend']['api_key']
            #     to = config["resend"]["signup_email"]
            # except KeyError as ke:
            #     msggg = "You did not pass a config_name, therefore, the default is to use resend, however, you need to add your resend api key to the emails.ini file."
            #     raise KeyError(msggg) from ke

            # _resend = install_n_import("resend")
            # import resend  # type: ignore
            # resend.api_key = api_key
            # r = resend.Emails.send({
            # "from": "onboarding@resend.dev",
            # "to": to,
            # "subject": subject,
            # "html": md2html(body=body)
            # })
            # return r

        else:
            config = dict(Email.get_source_of_truth()[config_name])
            tmp = Email(config=config)
            tmp.send_message(to=to, subject=subject, body=body)
            tmp.close()

    # @staticmethod
    # def send_m365(to: list[str], subject: str, body: Optional[str], body_file: Optional[str], body_content_type: Literal["HTML", "Text"], attachments: Optional[list[Path]] = None) -> None:
    #     if body_file is not None:
    #         assert body is None, "You cannot pass both body and body_file."
    #         body_file_path = Path(body_file)
    #         assert body_file_path.exists(), f"File not found: {body_file_path}"
    #     else:
    #         body_file_path = None
    #         assert body is not None, "You must pass either body or body_file."
    #     from crocodile.meta import Terminal

    #     to_str = ",".join(to)
    #     attachments_str = " ".join([f"--attachment {str(p)}" for p in attachments]) if attachments is not None else ""

    #     if body_file is not None:
    #         body_arg = f"--bodyContents @{body_file_path}"
    #     else:
    #         body_arg = f'"{body}"'
    #     cmd = f"""m365 outlook mail send --verbose --saveToSentItems --importance normal --bodyContentType {body_content_type} --bodyContents {body_arg} --subject "{subject}" --to {to_str} {attachments_str}"""
    #     response = Terminal().run(cmd, shell="powershell")
    #     response.print(desc="Email sending response")


# class PhoneNotification:  # security concerns: avoid using this.
#     def __init__(self, token: Optional[str]):
#         if token is None:
#             path = P.home().joinpath("dotfiles/machineconfig/phone_notification.ini")
#             ini = Read.ini(path)
#             token_ = ini["default"]["token"]
#         else:
#             token_ = token
#         pushbullet = install_n_import("pushbullet")
#         self.api = pushbullet.Pushbullet(token_)
#     def send_notification(self, title: str = "Note From Python", body: str = "A notfication"):
#         self.api.push_note(title=title, body=body)
#     @staticmethod
#     def open_website():
#         P(r"https://www.pushbullet.com/")()
#     @staticmethod  # https://www.youtube.com/watch?v=tbzPcKRZlHg
#     def try_me(bulletpoint_token: str):
#         n = PhoneNotification(bulletpoint_token)
#         n.send_notification()


if __name__ == "__main__":
    pass
