
import vt
import crocodile.toolbox as tb
import time
import pandas as pd
import platform
from rich.console import Console
# from rich.progress import track
from machineconfig.utils.utils import LIBRARY_ROOT
from machineconfig.jobs.python.python_linux_installers_all import get_installed_cli_apps


client = vt.Client(tb.P.home().joinpath("dotfiles/creds/tokens/virustotal").read_text().split("\n")[0])
console = Console()
safe_apps_records = LIBRARY_ROOT.joinpath(f"profile/records/{platform.system().lower()}/safe_cli_apps.csv")
safe_apps_url = LIBRARY_ROOT.joinpath(f"profile/records/{platform.system().lower()}/safe_cli_apps_url.txt")
safe_apps_remote = tb.P(f"myshare/{platform.system().lower()}/safe_cli_apps.zip")

def scan(path, pct=0.0):
    console.rule(f"Scanning {path}. {pct:.2f}% done")
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

    positive_pct = len(malicious) / len(df) * 100
    print(f"positive_ratio = {positive_pct:.1f} %")
    return positive_pct


def main():
    apps_raw = get_installed_cli_apps()

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
    for idx, app in enumerate(apps_filtered):
        try:
            res = scan(app, idx/len(apps_filtered)*100)
        except ValueError as ve:
            print(ve)
            res = None
        flags.append(res)

    res_df = pd.DataFrame({"app": apps_filtered.stem.list, "version": app_versions.values().list, "positive_pct": flags})

    apps_safe_df = res_df.query("positive_pct < 5")
    apps_safe = apps_raw.filter(lambda x: x.stem in list(apps_safe_df.app))
    # apps_safe_url = apps_safe.apply(lambda a_safe_app: a_safe_app.to_cloud("gdpo", remotepath=f"myshare/{platform.system().lower()}" / tb.P(a_safe_app.rel2home()), share=True), verbose=True, jobs=10)
    # res_df["url"] = apps_safe_url.apply(lambda x: x.as_posix() if type(x) == tb.P else None)
    tmp = tb.P.tmpdir()
    apps_safe.apply(lambda x: x.copy(folder=tmp))
    zipped = tmp.zip(content=True, name=safe_apps_remote.name)
    share_path = zipped.to_cloud("odg1", remotepath=safe_apps_remote, share=True)  # gdrive is suspicious of exe files.
    safe_apps_url.write_text(share_path.as_url_str())
    tmp.delete(sure=True)
    res_df.to_csv(safe_apps_records.create(parents_only=True), index=False)
    print(res_df)


if __name__ == '__main__':
    pass
