

from pathlib import Path

from rich.console import Console
from rich.text import Text
from rich.tree import Tree

from machineconfig.scripts.python.graph.visualize.graph_data import GraphNode, build_graph

STYLE_BY_KIND = {
    "root": "bold white",
    "group": "bold cyan",
    "command": "green",
}


def render_tree(
    *,
    path: Path | None = None,
    show_help: bool = True,
    show_aliases: bool = False,
    max_depth: int | None = None,
) -> None:
    root = build_graph(path)
    tree = build_rich_tree(root, show_help=show_help, show_aliases=show_aliases, max_depth=max_depth)
    Console().print(tree)


def build_rich_tree(
    root: GraphNode,
    *,
    show_help: bool = True,
    show_aliases: bool = False,
    max_depth: int | None = None,
) -> Tree:
    label = _format_label(root, show_help=show_help, show_aliases=show_aliases)
    tree = Tree(label)
    for child in root.children:
        _add_node(tree, child, show_help=show_help, show_aliases=show_aliases, max_depth=max_depth)
    return tree


def _add_node(
    parent: Tree,
    node: GraphNode,
    *,
    show_help: bool,
    show_aliases: bool,
    max_depth: int | None,
) -> None:
    if max_depth is not None and node.depth > max_depth:
        return
    label = _format_label(node, show_help=show_help, show_aliases=show_aliases)
    tree_node = parent.add(label)
    for child in node.children:
        _add_node(tree_node, child, show_help=show_help, show_aliases=show_aliases, max_depth=max_depth)


def _format_label(node: GraphNode, *, show_help: bool, show_aliases: bool) -> Text:
    style = STYLE_BY_KIND.get(node.kind, "white")
    name = node.name or node.command or node.id
    text = Text(name, style=style)

    if show_help:
        description = node.description.strip()
        if description and description != name:
            text.append(f" - {description}", style="dim")

    if show_aliases and node.aliases:
        alias_text = ", ".join(node.aliases)
        text.append(f" (aliases: {alias_text})", style="yellow")

    return text
