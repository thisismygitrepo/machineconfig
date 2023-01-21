
import vt
import crocodile.toolbox as tb
import time
import pandas as pd
import platform


client = vt.Client(tb.P.home().joinpath("dotfiles/creds/tokens/virustotal").read_text())


def scan(path):
    print(f"Scanning {path}")
    with open(str(path), "rb") as f:
        analysis = client.scan_file(f)

    while True:
        anal = client.get_object("/analyses/{}", analysis.id)
        print(anal.status)
        if anal.status == "completed": break
        else: print(f"waiting for scan of {path} ... ")
        time.sleep(30)

    df = pd.DataFrame(anal.results).T
    safe_flag = True
    for idx, row in df.iterrows():
        print(f"{idx} - {row['positives']} / {row['total']}")
        if row.result is None and row.category in ["undetected", "type-unsupported"]: continue
        else:
            print(f"Found {row}")
            safe_flag = False
        print(f"{idx} - {row['positives']} / {row['total']}")
    return safe_flag


def main():
    if platform.system() == "Windows":
        apps = tb.P.home().joinpath("AppData/Local/Microsoft/WindowsApps").search("*.exe")
    elif platform.system() == "Linux":
        apps = tb.P(r"/usr/local/bin").search("*")
    else:
        raise NotImplementedError("Not implemented for this OS")

    apps = tb.L([app for app in apps if app.size("kb") > 0.1])  # no symlinks like paint and wsl and bash

    flags = []
    for app in apps:
        res = scan(app)
        flags.append(res)

    res_df = pd.DataFrame({"app": apps.apply(lambda x: x.stem), "safe": flags})
    print(res_df)


if __name__ == '__main__':
    pass
