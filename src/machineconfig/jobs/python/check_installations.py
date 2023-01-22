
import vt
import crocodile.toolbox as tb
import time
import pandas as pd
import platform
from rich.console import Console
from rich.progress import track


client = vt.Client(tb.P.home().joinpath("dotfiles/creds/tokens/virustotal").read_text().split("\n")[0])
console = Console()


def scan(path):
    console.rule(f"Scanning {path}")
    with open(str(path), "rb") as f:
        analysis = client.scan_file(f)

    while True:
        with console.status(f"waiting for scan of {path} ... "):
            anal = client.get_object("/analyses/{}", analysis.id)
            # print(anal.status)
            if anal.status == "completed": break
            time.sleep(30)

    df = pd.DataFrame(anal.results).T
    malicious = []
    for idx, row in df.iterrows():
        if row.result is None and row.category in ["undetected", "type-unsupported", "failure", "timeout", "confirmed-timeout"]: continue
        else:
            tb.Struct(row.to_dict()).print(as_config=True, title=f"Found Category {row.category}")
            malicious.append(row)

    positive_ratio = len(malicious) / len(df) * 100
    print(f"positive_ratio = {positive_ratio:.1f} %")
    return positive_ratio


def main():
    if platform.system() == "Windows":
        apps = tb.P.home().joinpath("AppData/Local/Microsoft/WindowsApps").search("*.exe")
    elif platform.system() == "Linux":
        apps = tb.P(r"/usr/local/bin").search("*")
    else:
        raise NotImplementedError("Not implemented for this OS")

    apps = tb.L([app for app in apps if app.size("kb") > 0.1])  # no symlinks like paint and wsl and bash

    flags = []
    # for app in track(apps, description="App apps scanning..."):
    for app in apps:
        try:
            res = scan(app)
        except ValueError as ve:
            print(ve)
            res = None
        flags.append(res)

    res_df = pd.DataFrame({"app": apps.apply(lambda x: x.stem), "positive_ratio": flags})
    print(res_df)


if __name__ == '__main__':
    pass
