from dataclasses import dataclass
from typing import Optional, Annotated
import typer


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
