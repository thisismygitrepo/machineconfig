

from pathlib import Path
from typing import Annotated

import typer

from .graph_data import DEFAULT_GRAPH_PATH

GRAPH_HELP = f"Path to cli_graph.json (default: {DEFAULT_GRAPH_PATH})"

app = typer.Typer(help="Visualize the MachineConfig CLI graph in multiple formats.")


@app.command()
def tree(
    graph: Annotated[Path | None, typer.Option("--graph", "-g", help=GRAPH_HELP)] = None,
    show_help: Annotated[bool, typer.Option("--show-help/--no-show-help", help="Include help text in labels")] = True,
    show_aliases: Annotated[bool, typer.Option("--show-aliases/--no-show-aliases", help="Include aliases in labels")] = False,
    max_depth: Annotated[int | None, typer.Option("--max-depth", "-d", help="Limit depth of the tree")] = None,
) -> None:
    """Render a rich tree view in the terminal."""
    from .rich_tree import render_tree

    render_tree(path=graph, show_help=show_help, show_aliases=show_aliases, max_depth=max_depth)


@app.command()
def dot(
    graph: Annotated[Path | None, typer.Option("--graph", "-g", help=GRAPH_HELP)] = None,
    output: Annotated[Path | None, typer.Option("--output", "-o", help="Write DOT output to a file")] = None,
    include_help: Annotated[bool, typer.Option("--include-help/--no-include-help", help="Include help text in labels")] = True,
    max_depth: Annotated[int | None, typer.Option("--max-depth", "-d", help="Limit depth of the graph")] = None,
) -> None:
    """Export the graph as Graphviz DOT."""
    from .dot_export import render_dot

    dot_text = render_dot(path=graph, max_depth=max_depth, include_help=include_help)

    if output is None:
        print(dot_text)
        return

    output.write_text(dot_text, encoding="utf-8")
    print(f"Wrote {output}")


@app.command()
def sunburst(
    graph: Annotated[Path | None, typer.Option("--graph", "-g", help=GRAPH_HELP)] = None,
    output: Annotated[Path | None, typer.Option("--output", "-o", help="Write HTML or image output")] = None,
    max_depth: Annotated[int | None, typer.Option("--max-depth", "-d", help="Limit depth of the graph")] = None,
    template: Annotated[str, typer.Option("--template", help="Plotly template name")] = "plotly_white",
    height: Annotated[int, typer.Option("--height", help="Image height (for static output)")] = 900,
    width: Annotated[int, typer.Option("--width", help="Image width (for static output)")] = 1200,
) -> None:
    """Render a Plotly sunburst view."""
    from .plotly_views import render_plotly

    render_plotly(
        view="sunburst",
        path=graph,
        output=output,
        height=height,
        width=width,
        template=template,
        max_depth=max_depth,
    )


@app.command()
def treemap(
    graph: Annotated[Path | None, typer.Option("--graph", "-g", help=GRAPH_HELP)] = None,
    output: Annotated[Path | None, typer.Option("--output", "-o", help="Write HTML or image output")] = None,
    max_depth: Annotated[int | None, typer.Option("--max-depth", "-d", help="Limit depth of the graph")] = None,
    template: Annotated[str, typer.Option("--template", help="Plotly template name")] = "plotly_white",
    height: Annotated[int, typer.Option("--height", help="Image height (for static output)")] = 900,
    width: Annotated[int, typer.Option("--width", help="Image width (for static output)")] = 1200,
) -> None:
    """Render a Plotly treemap view."""
    from .plotly_views import render_plotly

    render_plotly(
        view="treemap",
        path=graph,
        output=output,
        height=height,
        width=width,
        template=template,
        max_depth=max_depth,
    )


@app.command()
def icicle(
    graph: Annotated[Path | None, typer.Option("--graph", "-g", help=GRAPH_HELP)] = None,
    output: Annotated[Path | None, typer.Option("--output", "-o", help="Write HTML or image output")] = None,
    max_depth: Annotated[int | None, typer.Option("--max-depth", "-d", help="Limit depth of the graph")] = None,
    template: Annotated[str, typer.Option("--template", help="Plotly template name")] = "plotly_white",
    height: Annotated[int, typer.Option("--height", help="Image height (for static output)")] = 900,
    width: Annotated[int, typer.Option("--width", help="Image width (for static output)")] = 1200,
) -> None:
    """Render a Plotly icicle view."""
    from .plotly_views import render_plotly

    render_plotly(
        view="icicle",
        path=graph,
        output=output,
        height=height,
        width=width,
        template=template,
        max_depth=max_depth,
    )


def main() -> None:
    app()


if __name__ == "__main__":
    main()
