"""CI
"""


import time
import platform
from rich.console import Console
from rich import inspect
# from rich.progress import track
from machineconfig.utils.utils import LIBRARY_ROOT, INSTALL_VERSION_ROOT
from machineconfig.utils.installer import get_installed_cli_apps
from crocodile.core import List as L, install_n_import
from crocodile.file_management import P
from crocodile.meta import Terminal
from tqdm import tqdm
from typing import Optional
from datetime import datetime
import csv


APP_SUMMARY_PATH = LIBRARY_ROOT.joinpath(f"profile/records/{platform.system().lower()}/apps_summary_report.csv")
CLOUD: str = "gdw"  # Read.ini(DEFAULTS_PATH)['general']['rclone_config_name']
# my onedrive doesn't allow sharing.


def scan(path: P, pct: float = 0.0):
    vt = install_n_import(library="vt", package="vt-py")
    client = vt.Client(P.home().joinpath("dotfiles/creds/tokens/virustotal").read_text().split("\n")[0])
    console = Console()
    console.rule(f"Scanning {path}. {pct:.2f}% done")
    if path.is_dir():
        print(f"📁 Skipping {path} as it is a directory.")
        return None
    with open(str(path), "rb") as f:
        analysis = client.scan_file(f)
    repeat_counter: int = 0
    while True:
        with console.status(f"waiting for scan of {path} ... "):
            try:
                anal = client.get_object("/analyses/{}", analysis.id)
                if anal.status == "completed": break
            except Exception as ex:  # type: ignore
                repeat_counter += 1
                if repeat_counter > 2:
                    raise ValueError(f"❌ Error in scanning {path}") from ex
                print("⚠️  Error in scanning, trying again...")
            time.sleep(30)
    
    # Convert results to list of dictionaries
    results_data = list(anal.results.values())
    malicious = []
    for result_item in results_data:
        # Convert result item to dictionary if it has attributes
        if hasattr(result_item, '__dict__'):
            result_dict = result_item.__dict__
        else:
            # Assume it already has the necessary attributes
            result_dict = {
                'result': getattr(result_item, 'result', None),
                'category': getattr(result_item, 'category', 'unknown')
            }
        
        if result_dict.get('result') is None and result_dict.get('category') in ["undetected", "type-unsupported", "failure", "timeout", "confirmed-timeout"]: 
            continue
        else:
            inspect(result_dict, value=False, title=f"🔍 Found Category {result_dict.get('category')}", docs=False, dunder=False, sort=False)
            malicious.append(result_item)
    
    positive_pct: float = round(number=len(malicious) / len(results_data) * 100, ndigits=1)
    print(f"""
{'=' * 50}
🔬 SCAN RESULTS | Positive ratio: {positive_pct:.1f}%
{'=' * 50}
""")
    return positive_pct, results_data


def main() -> None:
    apps_paths_tmp: L[P] = get_installed_cli_apps()
    versions_files_paths: L[P] = INSTALL_VERSION_ROOT.search()
    app_versions: list[Optional[str]] = []
    apps_paths_raw: L[P] = L([])
    for an_app in apps_paths_tmp:
        version_path = versions_files_paths.filter(lambda x: x.stem == an_app.stem)
        if len(version_path) == 1:
            app_versions.append(version_path.list[0].read_text())
            apps_paths_raw.append(an_app)
        # if an_app.stem in versions_files_paths.stem:
        #     app_versions.append(versions_files_paths.filter(lambda x: x.stem == an_app.stem.replace(".exe", "")).list[0].read_text())
        # else:
        #     print(f"🤔 Cloud not find a documented version for installation of {an_app.stem}, trying to get it from the app itself.")
        #     tmp = Terminal().run(f"{an_app.stem} --version", shell="powershell").capture().op_if_successfull_or_default(strict_err=False, strict_returcode=False)
        #     if tmp is not None: tmp = tmp.split("\n")[0]
        #     print(f"➡️ Found version `{tmp}` for {an_app.stem}.")
        #     app_versions.append(None)
    print(f"""
{'=' * 150}
🔍 TOOL CHECK | Checking tools (#{len(apps_paths_tmp)}) collected from `{INSTALL_VERSION_ROOT}`
{'=' * 150}
""")
    apps_paths_raw.print()
    positive_pct: list[Optional[float]] = []
    scan_time: list[str] = []
    detailed_results: list[dict[str, Optional[list]]] = []

    for idx, app in enumerate(apps_paths_raw):
        try: res = scan(path=app, pct=idx / len(apps_paths_raw) * 100)
        except ValueError as ve:
            print(f"❌ ERROR | {ve}")
            res = None
        if res is None:
            positive_pct.append(None)
            detailed_results.append({app.stem: None})
        else:
            ppct, results_data = res
            positive_pct.append(ppct)
            detailed_results.append({app.stem: results_data})
        scan_time.append(datetime.now().strftime("%Y-%m-%d %H:%M"))

    # Create list of dictionaries instead of DataFrame
    app_data = []
    for i, app_path in enumerate(apps_paths_raw):
        app_data.append({
            "app_name": app_path.stem,
            "version": app_versions[i],
            "positive_pct": positive_pct[i],
            "scan_time": scan_time[i],
            "app_path": app_path.collapseuser(strict=False).as_posix()
        })

    # Add app URLs
    for i, app_info in enumerate(tqdm(app_data, desc="Uploading apps")):
        apps_safe_url = upload(P(app_info["app_path"]).expanduser())
        app_info["app_url"] = apps_safe_url.as_posix() if type(apps_safe_url) is P else apps_safe_url

    # Write to CSV using standard library
    csv_path = APP_SUMMARY_PATH.with_suffix(".csv").create(parents_only=True)
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        if app_data:
            fieldnames = app_data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(app_data)

    # Create markdown table
    def format_app_table_markdown(data: list[dict]) -> str:
        if not data:
            return ""
        keys = list(data[0].keys())
        header = "|" + "|".join(f" {key} " for key in keys) + "|"
        separator = "|" + "|".join(" --- " for _ in keys) + "|"
        rows = []
        for row in data:
            row_values = [f" {str(row.get(key, ''))} " for key in keys]
            rows.append("|" + "|".join(row_values) + "|")
        return "\n".join([header, separator] + rows)

    markdown_content = format_app_table_markdown(app_data)
    APP_SUMMARY_PATH.with_suffix(".md").write_text(markdown_content)
    
    print(f"""
{'=' * 150}
📊 SAFETY REPORT | Summary of app scanning results
{'=' * 150}
""")
    print(markdown_content)


def upload(path: P):
    import call_function_with_timeout
    set_time_out = call_function_with_timeout.SetTimeout
    func_with_timeout = set_time_out(lambda: path.to_cloud(CLOUD, rel2home=True, share=True, os_specific=True), timeout=180)
    is_done, _is_timeout, _erro_message, results = func_with_timeout()
    if is_done: return results
    else: return None


class PrecheckedCloudInstaller:
    def __init__(self):
        install_n_import("gdown")
        # Read CSV using standard library
        self.data = []
        if APP_SUMMARY_PATH.exists():
            with open(APP_SUMMARY_PATH, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                self.data = list(reader)

    @staticmethod
    def download_google_links(url: str):
        # if "drive.google.com" in str(url): url = str(url).replace("open?", "uc?")
        # else: raise NotImplementedError("Only google drive is supported for now.")
        # return P(url).download(name=name)
        gdrive_id = P(url).parts[-1].split("id=")[1]
        gdown = install_n_import("gdown")
        result = P(gdown.download(id=gdrive_id)).absolute()
        return result

    @staticmethod
    def install_cli_apps(app_url: str):
        try:
            exe = PrecheckedCloudInstaller.download_google_links(app_url)
        except Exception as ex:  # type: ignore
            print(f"❌ ERROR | Failed downloading {app_url}: {ex}")
            return None
        if platform.system().lower() in ["linux", "darwin"]:
            Terminal().run(f"chmod +x {exe}")
            Terminal().run(f"mv {exe} /usr/local/bin/")
        elif platform.system().lower() == "windows":
            exe.move(folder=P.home().joinpath("AppData/Local/Microsoft/WindowsApps"), overwrite=True)
        return True

    def download_safe_apps(self, name: str="AllEssentials"):
        # if platform.system().lower() == "windows":
        #     from machineconfig.jobs.python.python_windows_installers_all import get_cli_py_installers
        #     cli_installers = get_cli_py_installers()
        # elif platform.system().lower() == "linux":
        #     from machineconfig.jobs.python.python_linux_installers_all import get_cli_py_installers
        #     cli_installers = get_cli_py_installers()
        # else: raise NotImplementedError(f"Platform {platform.system().lower()} is not supported yet.")

        if name == "AllEssentials":
            print(f"""
{'=' * 150}
📥 DOWNLOAD | Downloading {self.df.shape[0]} apps...
{'=' * 150}
""")
            print(self.df)
            _res = L(self.df.app_url).apply(PrecheckedCloudInstaller.install_cli_apps, jobs=20)
        else:
            app_url = self.df[self.df.app_name == name].iloc[0].app_url
            _res = PrecheckedCloudInstaller.install_cli_apps(app_url=app_url)

        # print("\n" * 3)
        # for item_flag, item_name in zip(res, self.df["app_name"]):
        #     if item_flag: print(f"✅ {item_name} is installed. 😁")
        #     else: print(f"❌ {item_name} failed to install for reasons explained in the log above, try manually.")


if __name__ == '__main__':
    pass
