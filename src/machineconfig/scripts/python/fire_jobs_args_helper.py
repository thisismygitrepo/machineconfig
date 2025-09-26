from dataclasses import dataclass
from typing import Optional, Any


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
    layout: bool = False


def extract_kwargs(args: FireJobArgs) -> dict[str, object]:
    """Extract kwargs from command line using -- separator.
    
    Returns empty dict since kwargs are now parsed directly from sys.argv
    using the -- separator pattern in the main function.
    """
    return {}


def parse_fire_args_from_argv() -> str:
    """Parse arguments after -- separator for Fire compatibility.
    
    Returns:
        String of Fire-compatible arguments to append to command
    """
    import sys
    
    if '--' in sys.argv:
        separator_index = sys.argv.index('--')
        fire_args = sys.argv[separator_index + 1:]
        # Join all Fire arguments - they should already be in Fire format
        return ' '.join(fire_args) if fire_args else ''
    
    return ''


def parse_fire_args_from_context(ctx: Any) -> str:
    """Parse Fire arguments from typer context.
    
    Args:
        ctx: Typer context containing raw arguments
        
    Returns:
        String of Fire-compatible arguments to append to command
    """
    # Get remaining args that weren't consumed by typer
    if hasattr(ctx, 'args') and ctx.args:
        args = ctx.args
        # Filter out the -- separator if present
        if args and args[0] == '--':
            args = args[1:]
        return ' '.join(args)
    return ''
