
import crocodile.toolbox as tb
import time
import pandas as pd
import platform
from rich.console import Console
# from rich.progress import track
from machineconfig.utils.utils import LIBRARY_ROOT
from machineconfig.jobs.python.python_linux_installers_all import get_installed_cli_apps
from tqdm import tqdm


vt = tb.install_n_import(package="vt", name="vt-py")
client = vt.Client(tb.P.home().joinpath("dotfiles/creds/tokens/virustotal").read_text().split("\n")[0])
safe_apps_records = LIBRARY_ROOT.joinpath(f"profile/records/{platform.system().lower()}/safe_cli_apps.json")
safe_apps_url = LIBRARY_ROOT.joinpath(f"profile/records/{platform.system().lower()}/safe_cli_apps_url.txt")
# safe_apps_remote = tb.P(f"myshare/{platform.system().lower()}/safe_cli_apps.zip")
cloud = "gdpo"


def scan(path, pct=0.0):
    console = Console()
    console.rule(f"Scanning {path}. {pct:.2f}% done")
    if path.is_dir():
        print(f"Skipping {path} as it is a directory.")
        return None
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
    apps_paths_raw = get_installed_cli_apps()

    app_versions = []
    versions = tb.P.home().joinpath(f"tmp_results/cli_tools_installers/versions").search()
    for an_app in apps_paths_raw:
        if an_app.stem in versions.stem: app_versions.append(versions.filter(lambda x: x.stem == an_app.stem.replace(".exe", ""))[0].read_text())
        else: app_versions.append(None)

    positive_pct = []
    # for app in track(apps, description="App apps scanning..."):
    for idx, app in enumerate(apps_paths_raw):
        try: res = scan(app, idx/len(apps_paths_raw)*100)
        except ValueError as ve:
            print(ve)
            res = None
        positive_pct.append(res)

    res_df = pd.DataFrame({"app_name": apps_paths_raw.stem.list, "version": app_versions, "positive_pct": positive_pct,
                           "app_path": apps_paths_raw.apply(lambda x: x.collapseuser(strict=False).as_posix()).list})

    apps_safe_df = res_df.query("positive_pct < 5")

    app_url = []
    for idx, row in tqdm(apps_safe_df.iterrows(), total=apps_safe_df.shape[0]):
        apps_safe_url = upload(tb.P(row["app_path"]).expanduser())
        app_url.append(apps_safe_url.as_posix() if type(apps_safe_url) == tb.P else apps_safe_url)
    res_df["app_url"] = app_url

    res_df.to_json(safe_apps_records.create(parents_only=True), index=False, orient='split')
    share_url = safe_apps_records.to_cloud(cloud, rel2home=True, share=True)
    safe_apps_url.write_text(share_url.as_posix())
    print(res_df)


def upload(path):
    tb.install_n_import("call_function_with_timeout")
    from call_function_with_timeout import SetTimeout
    def func():
        return path.to_cloud(cloud, rel2home=True, share=True)
    func_with_timeout = SetTimeout(func, timeout=180)
    is_done, is_timeout, erro_message, results = func_with_timeout()
    if is_done: return results
    else: return None


def download_rclone_links(url, name=None):
    if "drive.google.com" in str(url):
        url = str(url).replace("open?", "uc?")
    else: raise NotImplementedError("Only google drive is supported for now.")
    return tb.P(url).download(name=name)


def read_safe_apps_records(from_cloud=True):
    if from_cloud:
        file = download_rclone_links(safe_apps_url.read_text(), name=safe_apps_records.name)
    else:
        file = safe_apps_records
    tmp = file.readit()
    df = pd.DataFrame(tmp['data'], columns=tmp['columns'])
    return df


def download_safe_apps():
    df = read_safe_apps_records(from_cloud=True)

    if platform.system().lower() == "windows":
        from machineconfig.jobs.python.python_windows_installers_all import get_cli_py_installers
        cli_installers = get_cli_py_installers()
    elif platform.system().lower() == "linux":
        from machineconfig.jobs.python.python_linux_installers_all import get_cli_py_installers
        cli_installers = get_cli_py_installers()
    else: raise NotImplementedError(f"Platform {platform.system().lower()} is not supported yet.")
    for idx, row in df.iterrows():
        if row["app_url"] is None:
            print(f"{row['app_name']} url is not available, trying to download from its sources:")
            version = row["version"]
            if version is None:
                print(f"Version is not available, either, I can't trust the latest version. Skipping installation of this program.")
            else:
                tmp = cli_installers.filter(lambda x: x.stem == row["app_name"].replace(".exe", ""))
                if len(tmp) == 0: print(f"Can't find the installer for {row['app_name']}, skipping installation of this program.")
                else: tb.Read.py(tmp[0])["main"](version=version)
        else:
            name = row["app_name"]
            if platform.system().lower() == "windows" and not name.endswith(".exe"): name += ".exe"
            exe = download_rclone_links(row["app_url"], name=name)
            if platform.system().lower() == "linux":
                tb.Terminal().run(f"chmod +x {exe}")
                tb.Terminal().run(f"mv {exe} /usr/local/bin/")
            elif platform.system().lower() == "windows":
                exe.move(folder=tb.P.home().joinpath("AppData/Local/Microsoft/WindowsApps"))


if __name__ == '__main__':
    pass
