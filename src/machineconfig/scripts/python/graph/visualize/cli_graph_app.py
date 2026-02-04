

from pathlib import Path
from typing import Annotated

import typer

from machineconfig.scripts.python.graph.visualize.graph_paths import DEFAULT_GRAPH_PATH

GRAPH_HELP = f"Path to cli_graph.json (default: {DEFAULT_GRAPH_PATH})"


def tree(
    graph: Annotated[Path | None, typer.Option("--graph", "-g", help=GRAPH_HELP)] = None,
    show_help: Annotated[bool, typer.Option("--show-help/--no-show-help", help="Include help text in labels")] = True,
    show_aliases: Annotated[bool, typer.Option("--show-aliases/--no-show-aliases", help="Include aliases in labels")] = False,
    max_depth: Annotated[int | None, typer.Option("--max-depth", "-d", help="Limit depth of the tree")] = None,
) -> None:
    """Render a rich tree view in the terminal."""
    from machineconfig.scripts.python.graph.visualize.rich_tree import render_tree

    render_tree(path=graph, show_help=show_help, show_aliases=show_aliases, max_depth=max_depth)


def dot(
    graph: Annotated[Path | None, typer.Option("--graph", "-g", help=GRAPH_HELP)] = None,
    output: Annotated[Path | None, typer.Option("--output", "-o", help="Write DOT output to a file")] = None,
    include_help: Annotated[bool, typer.Option("--include-help/--no-include-help", help="Include help text in labels")] = True,
    max_depth: Annotated[int | None, typer.Option("--max-depth", "-d", help="Limit depth of the graph")] = None,
) -> None:
    """Export the graph as Graphviz DOT."""
    from machineconfig.scripts.python.graph.visualize.dot_export import render_dot

    dot_text = render_dot(path=graph, max_depth=max_depth, include_help=include_help)

    if output is None:
        print(dot_text)
        return

    output.write_text(dot_text, encoding="utf-8")
    print(f"Wrote {output}")


def sunburst(
    graph: Annotated[Path | None, typer.Option("--graph", "-g", help=GRAPH_HELP)] = None,
    output: Annotated[Path | None, typer.Option("--output", "-o", help="Write HTML or image output")] = None,
    max_depth: Annotated[int | None, typer.Option("--max-depth", "-d", help="Limit depth of the graph")] = None,
    template: Annotated[str, typer.Option("--template", help="Plotly template name")] = "plotly_dark",
    height: Annotated[int, typer.Option("--height", help="Image height (for static output)")] = 900,
    width: Annotated[int, typer.Option("--width", help="Image width (for static output)")] = 1200,
) -> None:
    """Render a Plotly sunburst view."""
    from machineconfig.scripts.python.graph.visualize.plotly_views import render_plotly

    render_plotly(
        view="sunburst",
        path=graph,
        output=output,
        height=height,
        width=width,
        template=template,
        max_depth=max_depth,
    )


def treemap(
    graph: Annotated[Path | None, typer.Option("--graph", "-g", help=GRAPH_HELP)] = None,
    output: Annotated[Path | None, typer.Option("--output", "-o", help="Write HTML or image output")] = None,
    max_depth: Annotated[int | None, typer.Option("--max-depth", "-d", help="Limit depth of the graph")] = None,
    template: Annotated[str, typer.Option("--template", help="Plotly template name")] = "plotly_dark",
    height: Annotated[int, typer.Option("--height", help="Image height (for static output)")] = 900,
    width: Annotated[int, typer.Option("--width", help="Image width (for static output)")] = 1200,
) -> None:
    """Render a Plotly treemap view."""
    from machineconfig.scripts.python.graph.visualize.plotly_views import render_plotly

    render_plotly(
        view="treemap",
        path=graph,
        output=output,
        height=height,
        width=width,
        template=template,
        max_depth=max_depth,
    )


def icicle(
    graph: Annotated[Path | None, typer.Option("--graph", "-g", help=GRAPH_HELP)] = None,
    output: Annotated[Path | None, typer.Option("--output", "-o", help="Write HTML or image output")] = None,
    max_depth: Annotated[int | None, typer.Option("--max-depth", "-d", help="Limit depth of the graph")] = None,
    template: Annotated[str, typer.Option("--template", help="Plotly template name")] = "plotly_dark",
    height: Annotated[int, typer.Option("--height", help="Image height (for static output)")] = 900,
    width: Annotated[int, typer.Option("--width", help="Image width (for static output)")] = 1200,
) -> None:
    """Render a Plotly icicle view."""
    from machineconfig.scripts.python.graph.visualize.plotly_views import render_plotly

    render_plotly(
        view="icicle",
        path=graph,
        output=output,
        height=height,
        width=width,
        template=template,
        max_depth=max_depth,
    )


def navigate():
    """📚 NAVIGATE command structure with TUI"""
    from machineconfig.utils.ssh_utils.abc import MACHINECONFIG_VERSION
    # import machineconfig.scripts.python.graph.visualize.helpers_navigator as navigator
    # path = Path(navigator.__file__).resolve().parent.joinpath("devops_navigator.py")
    # from machineconfig.utils.code import exit_then_run_shell_script
    # if Path.home().joinpath("code", "machineconfig").exists():
    #     executable = f"""--project "{str(Path.home().joinpath("code/machineconfig"))}" --with textual"""
    # else:
    #     executable = f"""--with "{MACHINECONFIG_VERSION},textual" """
    # exit_then_run_shell_script(f"""uv run {executable} {path}""")
    def func():
        from machineconfig.scripts.python.graph.visualize.helpers_navigator.devops_navigator import main as main_devops_navigator
        main_devops_navigator()
    from machineconfig.utils.code import get_shell_script_running_lambda_function, exit_then_run_shell_script
    if Path.home().joinpath("code", "machineconfig").exists():
        uv_with = ["textual"]
        uv_project_dir = str(Path.home().joinpath("code/machineconfig"))
    else:
        uv_with = [MACHINECONFIG_VERSION, "textual"]
        uv_project_dir = None
    shell_script, _pyfile = get_shell_script_running_lambda_function(lambda: func(),
            uv_with=uv_with, uv_project_dir=uv_project_dir)
    exit_then_run_shell_script(str(shell_script), strict=True)


def get_app() -> typer.Typer:
    cli_app = typer.Typer(
        help="🧭 [g] Visualize the MachineConfig CLI graph in multiple formats.",
        no_args_is_help=True,
        add_help_option=True,
        add_completion=False,
    )
    cli_app.command(name="tree", no_args_is_help=False, help="🌳 [t] Render a rich tree view in the terminal.")(tree)
    cli_app.command(name="t", no_args_is_help=False, help="Render a rich tree view in the terminal.", hidden=True)(tree)
    cli_app.command(name="dot", no_args_is_help=False, help="🧩 [d] Export the graph as Graphviz DOT.")(dot)
    cli_app.command(name="d", no_args_is_help=False, help="Export the graph as Graphviz DOT.", hidden=True)(dot)
    cli_app.command(name="sunburst", no_args_is_help=False, help="☀️ [s] Render a Plotly sunburst view.")(sunburst)
    cli_app.command(name="s", no_args_is_help=False, help="Render a Plotly sunburst view.", hidden=True)(sunburst)
    cli_app.command(name="treemap", no_args_is_help=False, help="🧱 [m] Render a Plotly treemap view.")(treemap)
    cli_app.command(name="m", no_args_is_help=False, help="Render a Plotly treemap view.", hidden=True)(treemap)
    cli_app.command(name="icicle", no_args_is_help=False, help="🧊 [i] Render a Plotly icicle view.")(icicle)
    cli_app.command(name="i", no_args_is_help=False, help="Render a Plotly icicle view.", hidden=True)(icicle)
    cli_app.command(name="tui", no_args_is_help=False, help="📚 [t] NAVIGATE command structure with TUI")(navigate)
    cli_app.command(name="t", no_args_is_help=False, help="NAVIGATE command structure with TUI", hidden=True)(navigate)
    return cli_app


def main() -> None:
    app = get_app()
    app()


if __name__ == "__main__":
    main()
