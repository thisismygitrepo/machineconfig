

from pathlib import Path

from machineconfig.scripts.python.graph.visualize.graph_data import (
    GraphNode,
    build_graph,
    iter_nodes,
)

KIND_COLORS = {
    "root": "#1f2937",
    "group": "#2563eb",
    "command": "#059669",
}

SUPPORTED_VIEWS = {"sunburst", "treemap", "icicle"}
IMAGE_EXTENSIONS = {".png", ".svg", ".pdf", ".jpg", ".jpeg", ".webp"}


def render_plotly(
    *,
    view: str,
    path: Path | None = None,
    output: Path | None = None,
    height: int = 900,
    width: int = 1200,
    template: str = "plotly_dark",
    max_depth: int | None = None,
) -> None:
    root = build_graph(path)
    fig = build_figure(root, view=view, template=template, max_depth=max_depth)

    if output is None:
        fig.show()
        return

    suffix = output.suffix.lower()
    if suffix in IMAGE_EXTENSIONS:
        fig.write_image(output, width=width, height=height, scale=2)
    else:
        fig.write_html(output, include_plotlyjs="cdn")

    print(f"Wrote {output}")


def build_figure(
    root: GraphNode,
    *,
    view: str,
    template: str = "plotly_dark",
    max_depth: int | None = None,
):
    view_key = view.lower().strip()
    if view_key not in SUPPORTED_VIEWS:
        raise ValueError(f"Unsupported view '{view}'. Choose from {sorted(SUPPORTED_VIEWS)}.")

    try:
        import plotly.graph_objects as go
    except ImportError as exc:
        raise RuntimeError("Plotly is required for this view. Install with: uv add plotly --dev") from exc

    ids, labels, parents, values, customdata, colors = _build_plotly_payload(root, max_depth=max_depth)

    hovertemplate = (
        "<b>%{label}</b><br>"
        "Command: %{customdata[0]}<br>"
        "Kind: %{customdata[1]}<br>"
        "Aliases: %{customdata[2]}<br>"
        "%{customdata[3]}<extra></extra>"
    )

    trace = None
    if view_key == "sunburst":
        trace = go.Sunburst(
            ids=ids,
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker={"colors": colors},
            customdata=customdata,
            hovertemplate=hovertemplate,
        )
    elif view_key == "treemap":
        trace = go.Treemap(
            ids=ids,
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker={"colors": colors},
            customdata=customdata,
            hovertemplate=hovertemplate,
        )
    elif view_key == "icicle":
        trace = go.Icicle(
            ids=ids,
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker={"colors": colors},
            customdata=customdata,
            hovertemplate=hovertemplate,
        )

    fig = go.Figure(trace)
    fig.update_layout(
        template=template,
        margin={"l": 20, "r": 20, "t": 50, "b": 20},
        title={"text": f"CLI Graph - {view_key.title()}", "x": 0.5},
        height=900,
    )
    return fig


def _build_plotly_payload(root: GraphNode, *, max_depth: int | None = None):
    ids: list[str] = []
    labels: list[str] = []
    parents: list[str] = []
    values: list[int] = []
    customdata: list[list[str]] = []
    colors: list[str] = []

    for node, parent in iter_nodes(root):
        if max_depth is not None and node.depth > max_depth:
            continue
        if parent is not None and max_depth is not None and parent.depth > max_depth:
            continue

        ids.append(node.id)
        labels.append(node.name or node.command or node.id)
        parents.append(parent.id if parent is not None else "")
        values.append(node.leaf_count)

        alias_text = ", ".join(node.aliases) if node.aliases else "-"
        description = node.long_description or node.description or ""
        customdata.append([node.command, node.kind, alias_text, description])
        colors.append(KIND_COLORS.get(node.kind, "#94a3b8"))

    return ids, labels, parents, values, customdata, colors
