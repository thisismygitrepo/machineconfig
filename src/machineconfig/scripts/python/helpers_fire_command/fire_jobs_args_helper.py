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
    marimo: bool = False
    submit_to_cloud: bool = False
    remote: bool = False
    module: bool = False
    streamlit: bool = False
    environment: str = ""
    holdDirectory: bool = False
    PathExport: bool = False
    git_pull: bool = False
    optimized: bool = False
    zellij_tab: Optional[str] = None
    watch: bool = False


def extract_kwargs(args: FireJobArgs) -> dict[str, object]:
    """Extract kwargs from command line arguments in Fire format.
    
    Parses Fire-like arguments (e.g., --a=2, --name=value) from sys.argv
    and returns them as a dictionary.
    
    Returns:
        Dictionary mapping argument names to their values
    """
    import sys
    
    kwargs: dict[str, object] = {}
    
    # Look for Fire-style arguments in sys.argv
    for arg in sys.argv:
        # Skip the -- separator
        if arg == '--':
            continue
            
        # Match patterns like --key=value or --key value (but we'll focus on --key=value)
        if arg.startswith('--') and '=' in arg:
            key, value = arg[2:].split('=', 1)  # Remove -- prefix and split on first =
            
            # Try to convert value to appropriate type
            kwargs[key] = _convert_value_type(value)
        elif arg.startswith('--') and '=' not in arg:
            # Handle boolean flags like --debug
            key = arg[2:]  # Remove -- prefix
            
            # Skip empty key (this would happen if someone just used '--')
            if not key:
                continue
                
            # Check if next argument exists and doesn't start with --
            arg_index = sys.argv.index(arg)
            if arg_index + 1 < len(sys.argv) and not sys.argv[arg_index + 1].startswith('--'):
                # Next argument is the value
                value = sys.argv[arg_index + 1]
                kwargs[key] = _convert_value_type(value)
            else:
                # It's a boolean flag
                kwargs[key] = True
                
    return kwargs


def _convert_value_type(value: str) -> object:
    """Convert string value to appropriate Python type."""
    # Try to convert to int
    try:
        if '.' not in value and 'e' not in value.lower():
            return int(value)
    except ValueError:
        pass
    
    # Try to convert to float
    try:
        return float(value)
    except ValueError:
        pass
    
    # Try to convert boolean strings
    if value.lower() in ('true', '1', 'yes', 'on'):
        return True
    elif value.lower() in ('false', '0', 'no', 'off'):
        return False
    
    # Try to convert None
    if value.lower() == 'none':
        return None
    
    # Try to parse as list (comma-separated values)
    if ',' in value:
        items = [_convert_value_type(item.strip()) for item in value.split(',')]
        return items
    
    # Return as string if no conversion possible
    return value


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
