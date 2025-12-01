"""Sessions management commands - lazy loading subcommands."""

from typing import Optional, Literal, Annotated
import typer


def balance_load(
    layout_path: Annotated[str, typer.Argument(..., help="Path to the layout.json file")],
    max_thresh: Annotated[int, typer.Option(..., "--max-threshold", "-m", help="Maximum tabs per layout")],
    thresh_type: Annotated[Literal["number", "n", "weight", "w"], typer.Option(..., "--threshold-type", "-t", help="Threshold type")],
    breaking_method: Annotated[Literal["moreLayouts", "ml", "combineTabs", "ct"], typer.Option(..., "--breaking-method", "-b", help="Breaking method")],
    output_path: Annotated[Optional[str], typer.Option(..., "--output-path", "-o", help="Path to write the adjusted layout.json file")] = None,
) -> None:
    """Adjust layout file to limit max tabs per layout, etc."""
    from machineconfig.scripts.python.helpers.helpers_sessions.sessions_impl import balance_load as impl
    impl(layout_path=layout_path, max_thresh=max_thresh, thresh_type=thresh_type, breaking_method=breaking_method, output_path=output_path)


def run(
    ctx: typer.Context,
    layout_path: Annotated[Optional[str], typer.Argument(..., help="Path to the layout.json file")] = None,
    max_tabs: Annotated[int, typer.Option(..., "--max-tabs", "-mt", help="A Sanity checker that throws an error if any layout exceeds the maximum number of tabs to launch.")] = 10,
    max_layouts: Annotated[int, typer.Option(..., "--max-layouts", "-ml", help="A Sanity checker that throws an error if the total number of *parallel layouts exceeds this number.")] = 10,
    sleep_inbetween: Annotated[float, typer.Option(..., "--sleep-inbetween", "-si", help="Sleep time in seconds between launching layouts")] = 1.0,
    monitor: Annotated[bool, typer.Option(..., "--monitor", "-m", help="Monitor the layout sessions for completion")] = False,
    parallel: Annotated[bool, typer.Option(..., "--parallel", "-p", help="Launch multiple layouts in parallel")] = False,
    kill_upon_completion: Annotated[bool, typer.Option(..., "--kill-upon-completion", "-k", help="Kill session(s) upon completion (only relevant if monitor flag is set)")] = False,
    choose: Annotated[Optional[str], typer.Option(..., "--choose", "-c", help="Comma separated names of layouts to be selected from the layout file passed")] = None,
    choose_interactively: Annotated[bool, typer.Option(..., "--choose-interactively", "-i", help="Select layouts interactively")] = False,
    subsitute_home: Annotated[bool, typer.Option(..., "--substitute-home", "-sh", help="Substitute ~ and $HOME in layout file with actual home directory path")] = False,
) -> None:
    """Launch terminal sessions based on a layout configuration file."""
    if layout_path is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()
    from machineconfig.scripts.python.helpers.helpers_sessions.sessions_impl import run_layouts
    try:
        run_layouts(layout_path=layout_path, max_tabs=max_tabs, max_layouts=max_layouts, sleep_inbetween=sleep_inbetween, monitor=monitor, parallel=parallel, kill_upon_completion=kill_upon_completion, choose=choose, choose_interactively=choose_interactively, subsitute_home=subsitute_home)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(1) from e


def create_template(
    name: Annotated[Optional[str], typer.Argument(..., help="Name of the layout template to create")] = None,
    num_tabs: Annotated[int, typer.Option(..., "--num-tabs", "-t", help="Number of tabs to include in the template")] = 3,
) -> None:
    """Create a layout template file."""
    from machineconfig.scripts.python.helpers.helpers_sessions.sessions_impl import create_template as impl
    impl(name=name, num_tabs=num_tabs)


def create_from_function(
    num_process: Annotated[int, typer.Option(..., "--num-process", "-n", help="Number of parallel processes to run")],
    path: Annotated[str, typer.Option(..., "--path", "-p", help="Path to a Python or Shell script file or a directory containing such files")] = ".",
    function: Annotated[Optional[str], typer.Option(..., "--function", "-f", help="Function to run from the Python file. If not provided, you will be prompted to choose.")] = None,
) -> None:
    """Create a layout from a function to run in multiple processes."""
    from machineconfig.scripts.python.helpers.helpers_sessions.sessions_multiprocess import create_from_function as impl
    impl(num_process=num_process, path=path, function=function)


def get_app() -> typer.Typer:
    layouts_app = typer.Typer(help="Layouts management subcommands", no_args_is_help=True, add_help_option=True, add_completion=False)

    layouts_app.command("create-from-function", no_args_is_help=True, short_help="[c] Create a layout from a function")(create_from_function)
    layouts_app.command("c", no_args_is_help=True, hidden=True)(create_from_function)

    layouts_app.command("run", no_args_is_help=True, help=run.__doc__, short_help="[r] Run the selected layout(s)")(run)
    layouts_app.command("r", no_args_is_help=True, help=run.__doc__, hidden=True)(run)

    layouts_app.command("balance-load", no_args_is_help=True, help=balance_load.__doc__, short_help="[b] Balance the load across sessions")(balance_load)
    layouts_app.command("b", no_args_is_help=True, help=balance_load.__doc__, hidden=True)(balance_load)

    layouts_app.command("create-template", no_args_is_help=False, help=create_template.__doc__, short_help="[t] Create a layout template file")(create_template)
    layouts_app.command("t", no_args_is_help=False, help=create_template.__doc__, hidden=True)(create_template)
    return layouts_app


def main() -> None:
    layouts_app = get_app()
    layouts_app()


if __name__ == "__main__":
    pass
