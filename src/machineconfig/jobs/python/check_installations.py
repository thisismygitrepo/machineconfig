
import vt
import crocodile.toolbox as tb
import time
import pandas as pd
import platform
from rich.console import Console
from rich.progress import track

from machineconfig.utils.utils import LIBRARY_ROOT


client = vt.Client(tb.P.home().joinpath("dotfiles/creds/tokens/virustotal").read_text().split("\n")[0])
console = Console()


def get_cli_apps():
    if platform.system() == "Windows":
        apps = tb.P.home().joinpath("AppData/Local/Microsoft/WindowsApps").search("*.exe", not_in=["notepad", "ZoomIt"])
    elif platform.system() == "Linux":
        apps = tb.P(r"/usr/local/bin").search("*")
    else:
        raise NotImplementedError("Not implemented for this OS")
    apps = tb.L([app for app in apps if app.size("kb") > 0.1])  # no symlinks like paint and wsl and bash
    return apps


def scan(path):
    console.rule(f"Scanning {path}")
    with open(str(path), "rb") as f:
        analysis = client.scan_file(f)

    repeat_counter = 0
    while True:
        with console.status(f"waiting for scan of {path} ... "):

            try:
                anal = client.get_object("/analyses/{}", analysis.id)
                # print(anal.status)
                if anal.status == "completed": break
            except:
                repeat_counter += 1
                if repeat_counter > 2:
                    raise ValueError(f"Error in scanning {path}")
                print(f"Error in scanning, trying again.")

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
    apps_raw = get_cli_apps()

    versions = tb.P.home().joinpath(f"tmp_results/cli_tools_installers/versions").search()
    app_versions = tb.S()
    for an_app in apps_raw:
        if an_app.stem in versions.stem:
            app_versions[an_app] = versions.filter(lambda x: x.stem == an_app.stem.replace(".exe", ""))[0].read_text()
    apps_filtered = app_versions.keys()
    print(f"The following apps have been skipped for lacking version information registeration at install time. Only versioned apps can be scanned and documented. Otherwise it is pointless.")
    for item in apps_raw:
        if item not in apps_filtered: print(item.stem)

    flags = []
    # for app in track(apps, description="App apps scanning..."):
    for app in apps_filtered:
        try:
            res = scan(app)
        except ValueError as ve:
            print(ve)
            res = None
        flags.append(res)

    res_df = pd.DataFrame({"app": apps_filtered.stem, "version": app_versions.values(), "positive_ratio": flags})
    res_df.to_csv(tb.P.home().joinpath(f"tmp_results/cli_tools_installers/safe_cli_apps.csv"))
    res_df.to_csv(LIBRARY_ROOT.joinpath(f"jobs/python/archive/safe_cli_apps.csv"))
    print(res_df)


def get_version(app):
    res = tb.Terminal().run(f"{app} --version", shell="powershell").op
    if res == "":
        return None
    else:
        return res.replace("\n", " ")


def export_safe_versions():
    apps = get_cli_apps()
    versions = apps.apply(get_version, verbose=True).list
    df = pd.DataFrame({"app": apps.stem, "version": versions})
    # tb.P.home().joinpath("dotfiles/creds/tokens/safe_apps").write_text("\n".join(safe_apps))
    return df


if __name__ == '__main__':
    pass
