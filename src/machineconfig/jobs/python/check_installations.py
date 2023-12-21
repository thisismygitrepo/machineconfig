
"""CI
"""

import crocodile.toolbox as tb
import time
import pandas as pd
import platform
from rich.console import Console
# from rich.progress import track
from machineconfig.utils.utils import LIBRARY_ROOT, INSTALL_VERSION_ROOT
from machineconfig.utils.installer import get_installed_cli_apps
from tqdm import tqdm
from typing import Optional


APP_SUMMARY_PATH = LIBRARY_ROOT.joinpath(f"profile/records/{platform.system().lower()}/apps_summary_report.csv")
CLOUD: str = "gdw"  # tb.Read.ini(DEFAULTS_PATH)['general']['rclone_config_name']
# my onedrive doesn't allow sharing.


def scan(path: tb.P, pct: float = 0.0):
    vt = tb.install_n_import(library="vt", package="vt-py")
    client = vt.Client(tb.P.home().joinpath("dotfiles/creds/tokens/virustotal").read_text().split("\n")[0])
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
            except Exception as ex:  # type: ignore
                repeat_counter += 1
                if repeat_counter > 2:
                    raise ValueError(f"Error in scanning {path}") from ex
                print(f"Error in scanning, trying again.")
            time.sleep(30)
    df = pd.DataFrame(anal.results).T
    malicious = []
    for _idx, row in df.iterrows():
        if row.result is None and row.category in ["undetected", "type-unsupported", "failure", "timeout", "confirmed-timeout"]: continue
        else:
            tb.Struct(row.to_dict()).print(as_config=True, title=f"Found Category {row.category}")
            malicious.append(row)
    positive_pct = round(len(malicious) / len(df) * 100, 1)
    print(f"positive_ratio = {positive_pct:.1f} %")
    return positive_pct, df


def main() -> None:
    apps_paths_tmp: tb.List[tb.P] = get_installed_cli_apps()
    versions_files_paths: tb.L[tb.P] = INSTALL_VERSION_ROOT.search()
    app_versions: list[Optional[str]] = []
    apps_paths_raw: tb.L[tb.P] = tb.L([])
    for an_app in versions_files_paths:
        exe_path = apps_paths_tmp.filter(lambda x: x.stem == an_app.stem)
        if len(exe_path) == 1:
            app_versions.append(an_app.read_text())
            apps_paths_raw.append(exe_path.list[0])
        # if an_app.stem in versions_files_paths.stem:
        #     app_versions.append(versions_files_paths.filter(lambda x: x.stem == an_app.stem.replace(".exe", "")).list[0].read_text())
        # else:
        #     print(f"🤔 Cloud not find a documented version for installation of {an_app.stem}, trying to get it from the app itself.")
        #     tmp = tb.Terminal().run(f"{an_app.stem} --version", shell="powershell").capture().op_if_successfull_or_default(strict_err=False, strict_returcode=False)
        #     if tmp is not None: tmp = tmp.split("\n")[0]
        #     print(f"➡️ Found version `{tmp}` for {an_app.stem}.")
        #     app_versions.append(None)
    print(f"Checking tools collected from `{INSTALL_VERSION_ROOT}`:")
    apps_paths_raw.print()
    positive_pct: list[Optional[float]] = []
    detailed_results: list[dict[str, Optional[pd.DataFrame]]] = []
    for idx, app in enumerate(apps_paths_raw):
        try: res = scan(path=app, pct=idx / len(apps_paths_raw) * 100)
        except ValueError as ve:
            print(ve)
            res = None
        if res is None:
            positive_pct.append(None)
            detailed_results.append({app.stem: None})
        else:
            ppct, df = res
            positive_pct.append(ppct)
            detailed_results.append({app.stem: df})

    res_df = pd.DataFrame({"app_name": apps_paths_raw.apply(lambda x: x.stem).list, "version": app_versions, "positive_pct": positive_pct,
                                "app_path": apps_paths_raw.apply(lambda x: x.collapseuser(strict=False).as_posix()).list})

    app_url: list[Optional[str]] = []
    for idx, row in tqdm(res_df.iterrows(), total=res_df.shape[0]):
        apps_safe_url = upload(tb.P(str(row["app_path"])).expanduser())
        app_url.append(apps_safe_url.as_posix() if type(apps_safe_url) is tb.P else apps_safe_url)
    res_df["app_url"] = app_url
    res_df.to_csv(APP_SUMMARY_PATH.with_suffix(".csv").create(parents_only=True), index=False)
    APP_SUMMARY_PATH.with_suffix(".md").write_text(res_df.to_markdown())
    print(f"Safety Report:")
    print(res_df)


def upload(path: tb.P):
    set_time_out = tb.install_n_import("call_function_with_timeout").SetTimeout
    func_with_timeout = set_time_out(lambda: path.to_cloud(CLOUD, rel2home=True, share=True, os_specific=True), timeout=180)
    is_done, _is_timeout, _erro_message, results = func_with_timeout()
    if is_done: return results
    else: return None


class PrecheckedCloudInstaller:
    def __init__(self):
        tb.install_n_import("gdown")
        self.df = pd.read_csv(APP_SUMMARY_PATH)

    @staticmethod
    def download_google_links(url: str):
        # if "drive.google.com" in str(url): url = str(url).replace("open?", "uc?")
        # else: raise NotImplementedError("Only google drive is supported for now.")
        # return tb.P(url).download(name=name)
        gdrive_id = tb.P(url).parts[-1].split("id=")[1]
        gdown = tb.install_n_import("gdown")
        result = tb.P(gdown.download(id=gdrive_id)).absolute()
        return result

    @staticmethod
    def install_cli_apps(app_url: str):
        try:
            exe = PrecheckedCloudInstaller.download_google_links(app_url)
        except Exception as ex:  # type: ignore
            print(f"Error in downloading {app_url} {ex}")
            return None
        if platform.system().lower() == "linux":
            tb.Terminal().run(f"chmod +x {exe}")
            tb.Terminal().run(f"mv {exe} /usr/local/bin/")
        elif platform.system().lower() == "windows":
            exe.move(folder=tb.P.home().joinpath("AppData/Local/Microsoft/WindowsApps"), overwrite=True)
        return True

    def download_safe_apps(self, name: str = "AllEssentials"):
        # if platform.system().lower() == "windows":
        #     from machineconfig.jobs.python.python_windows_installers_all import get_cli_py_installers
        #     cli_installers = get_cli_py_installers()
        # elif platform.system().lower() == "linux":
        #     from machineconfig.jobs.python.python_linux_installers_all import get_cli_py_installers
        #     cli_installers = get_cli_py_installers()
        # else: raise NotImplementedError(f"Platform {platform.system().lower()} is not supported yet.")

        if name == "AllEssentials":
            print(f"Downloading {self.df.shape[0]} apps ...")
            print(self.df)
            _res = tb.L(self.df.app_url).apply(PrecheckedCloudInstaller.install_cli_apps, jobs=20)
        else:
            app_url = self.df[self.df.app_name == name].iloc[0].app_url
            _res = PrecheckedCloudInstaller.install_cli_apps(app_url=app_url)

        # print("\n" * 3)
        # for item_flag, item_name in zip(res, self.df["app_name"]):
        #     if item_flag: print(f"✅ {item_name} is installed. 😁")
        #     else: print(f"❌ {item_name} failed to install for reasons explained in the log above, try manually.")


if __name__ == '__main__':
    pass
