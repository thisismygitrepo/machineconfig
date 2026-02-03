

from pathlib import Path

from machineconfig.scripts.python.graph.visualize.graph_data import (
    GraphNode,
    build_graph,
    iter_nodes,
)

KIND_STYLES = {
    "root": {"shape": "doubleoctagon", "fillcolor": "#f1f1f1", "color": "#555555"},
    "group": {"shape": "box", "fillcolor": "#dbeafe", "color": "#2563eb"},
    "command": {"shape": "box", "fillcolor": "#dcfce7", "color": "#15803d"},
}


def render_dot(
    *,
    path: Path | None = None,
    max_depth: int | None = None,
    include_help: bool = True,
) -> str:
    root = build_graph(path)
    return build_dot(root, max_depth=max_depth, include_help=include_help)


def build_dot(root: GraphNode, *, max_depth: int | None = None, include_help: bool = True) -> str:
    lines: list[str] = [
        "digraph cli_graph {",
        "  graph [rankdir=LR, splines=true, bgcolor=\"white\"];",
        "  node [shape=box, style=\"rounded,filled\", fontname=\"Helvetica\", fontsize=10, color=\"#333333\"];",
        "  edge [color=\"#999999\"];",
    ]

    for node, parent in iter_nodes(root):
        if max_depth is not None and node.depth > max_depth:
            continue

        style = KIND_STYLES.get(node.kind, KIND_STYLES["command"])
        label = _node_label(node, include_help=include_help)
        lines.append(
            "  \"{node_id}\" [label=\"{label}\", shape=\"{shape}\", fillcolor=\"{fill}\", color=\"{color}\"];".format(
                node_id=_dot_escape(node.id),
                label=_dot_escape(label),
                shape=style["shape"],
                fill=style["fillcolor"],
                color=style["color"],
            )
        )

        if parent is not None and (max_depth is None or parent.depth <= max_depth):
            lines.append(
                "  \"{parent}\" -> \"{child}\";".format(
                    parent=_dot_escape(parent.id),
                    child=_dot_escape(node.id),
                )
            )

    lines.append("}")
    return "\n".join(lines)


def _node_label(node: GraphNode, *, include_help: bool) -> str:
    name = node.name or node.command or node.id
    if not include_help:
        return name

    description = node.description.strip()
    if description and description != name:
        return f"{name}\n{_truncate(description, 72)}"
    return name


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _dot_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n")
