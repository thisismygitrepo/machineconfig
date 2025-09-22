from dataclasses import dataclass
from typing import Optional
import argparse


@dataclass
class FireJobArgs:
    """Type-safe dataclass for fire_jobs command line arguments."""

    path: str = "."
    function: Optional[str] = None
    ve: str = ""
    cmd: bool = False
    interactive: bool = False
    debug: bool = False
    choose_function: bool = False
    loop: bool = False
    jupyter: bool = False
    submit_to_cloud: bool = False
    remote: bool = False
    module: bool = False
    streamlit: bool = False
    environment: str = ""
    holdDirectory: bool = False
    PathExport: bool = False
    git_pull: bool = False
    optimized: bool = False
    Nprocess: int = 1
    zellij_tab: Optional[str] = None
    watch: bool = False
    kw: Optional[list[str]] = None
    layout: bool = False


def get_args() -> FireJobArgs:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", type=str, help="The directory containing the jobs", default=".")
    parser.add_argument("function", nargs="?", type=str, help="Fuction to run", default=None)
    parser.add_argument("--ve", "-v", type=str, help="virtual enviroment name", default="")
    parser.add_argument("--cmd", "-B", action="store_true", help="Create a cmd fire command to launch the the job asynchronously.")
    parser.add_argument("--interactive", "-i", action="store_true", help="Whether to run the job interactively using IPython")
    parser.add_argument("--debug", "-d", action="store_true", help="debug")
    parser.add_argument("--choose_function", "-c", action="store_true", help="debug")
    parser.add_argument("--loop", "-l", action="store_true", help="infinite recusion (runs again after completion/interruption)")
    parser.add_argument("--jupyter", "-j", action="store_true", help="open in a jupyter notebook")
    parser.add_argument("--submit_to_cloud", "-C", action="store_true", help="submit to cloud compute")
    parser.add_argument("--remote", "-r", action="store_true", help="launch on a remote machine")
    parser.add_argument("--module", "-m", action="store_true", help="launch the main file")
    parser.add_argument("--streamlit", "-S", action="store_true", help="run as streamlit app")
    parser.add_argument("--environment", "-E", type=str, help="Choose ip, localhost, hostname or arbitrary url", default="")
    parser.add_argument("--holdDirectory", "-D", action="store_true", help="hold current directory and avoid cd'ing to the script directory")
    parser.add_argument("--PathExport", "-P", action="store_true", help="augment the PYTHONPATH with repo root.")
    parser.add_argument("--git_pull", "-g", action="store_true", help="Start by pulling the git repo")
    parser.add_argument("--optimized", "-O", action="store_true", help="Run the optimized version of the function")
    parser.add_argument("--Nprocess", "-p", type=int, help="Number of processes to use", default=1)
    parser.add_argument("--zellij_tab", "-z", type=str, dest="zellij_tab", help="open in a new zellij tab")
    parser.add_argument("--watch", "-w", action="store_true", help="watch the file for changes")
    parser.add_argument("--kw", nargs="*", default=None, help="keyword arguments to pass to the function in the form of k1 v1 k2 v2 ... (meaning k1=v1, k2=v2, etc)")
    parser.add_argument("--layout", "-L", action="store_true", help="use layout configuration (Zellij Or WindowsTerminal)")

    try:
        args_raw = parser.parse_args()
    except Exception as ex:
        print(f"❌ Failed to parse arguments: {ex}")
        parser.print_help()
        raise ex
    args = FireJobArgs(**vars(args_raw))
    return args


def extract_kwargs(args: FireJobArgs) -> dict[str, object]:
    str2obj = {"True": True, "False": False, "None": None}
    if args.kw is not None:
        assert len(args.kw) % 2 == 0, f"args.kw must be a list of even length. Got {len(args.kw)}"
        kwargs = dict(zip(args.kw[::2], args.kw[1::2]))
        kwargs: dict[str, object]
        for key, value in kwargs.items():
            if value in str2obj:
                kwargs[key] = str2obj[str(value)]
        if args.function is None:  # if user passed arguments and forgot to pass function, then assume they want to run the main function.
            args.choose_function = True
    else:
        kwargs = {}
    return kwargs
