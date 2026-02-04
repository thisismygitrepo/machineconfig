

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Iterator

from machineconfig.scripts.python.graph.visualize.graph_paths import DEFAULT_GRAPH_PATH


@dataclass
class GraphNode:
    id: str
    name: str
    kind: str
    command: str
    description: str
    long_description: str
    aliases: list[str]
    depth: int
    children: list["GraphNode"] = field(default_factory=list)
    leaf_count: int = 1

    @property
    def is_group(self) -> bool:
        return self.kind in {"group", "root"}


def load_cli_graph(path: Path | None = None) -> dict[str, Any]:
    graph_path = path or DEFAULT_GRAPH_PATH
    return json.loads(graph_path.read_text(encoding="utf-8"))


def build_graph(path: Path | None = None) -> GraphNode:
    data = load_cli_graph(path)
    root = data.get("root") or {}
    root_name = root.get("name") or "root"
    node = _build_node(root, parent_tokens=[], depth=0, fallback_name=root_name)
    _compute_leaf_counts(node)
    return node


def iter_nodes(root: GraphNode) -> Iterator[tuple[GraphNode, GraphNode | None]]:
    stack: list[tuple[GraphNode, GraphNode | None]] = [(root, None)]
    while stack:
        node, parent = stack.pop()
        yield node, parent
        for child in reversed(node.children):
            stack.append((child, node))


def _build_node(
    node: dict[str, Any],
    *,
    parent_tokens: list[str],
    depth: int,
    fallback_name: str,
) -> GraphNode:
    kind = node.get("kind") or "command"
    name = node.get("name") or fallback_name
    tokens = parent_tokens + ([name] if name else [])
    command = " ".join(tokens).strip()
    node_id = command or _fallback_id(parent_tokens, depth)

    description = _node_description(node)
    long_description = _node_long_description(node, description)
    aliases = _node_aliases(node)

    children_data = node.get("children") or []
    children = [
        _build_node(child, parent_tokens=tokens, depth=depth + 1, fallback_name=f"node-{depth + 1}")
        for child in children_data
    ]

    return GraphNode(
        id=node_id,
        name=name,
        kind=kind,
        command=command,
        description=description,
        long_description=long_description,
        aliases=aliases,
        depth=depth,
        children=children,
    )


def _compute_leaf_counts(node: GraphNode) -> int:
    if not node.children:
        node.leaf_count = 1
        return 1
    total = 0
    for child in node.children:
        total += _compute_leaf_counts(child)
    node.leaf_count = total
    return total


def _node_description(node: dict[str, Any]) -> str:
    if node.get("kind") == "group":
        return (
            (node.get("app") or {}).get("help")
            or node.get("help")
            or node.get("doc")
            or node.get("name")
            or ""
        )
    return (
        node.get("short_help")
        or node.get("help")
        or node.get("doc")
        or node.get("name")
        or ""
    )


def _node_long_description(node: dict[str, Any], fallback: str) -> str:
    if node.get("kind") == "group":
        return (
            (node.get("app") or {}).get("help")
            or node.get("help")
            or node.get("doc")
            or fallback
        )
    return node.get("help") or node.get("doc") or fallback


def _node_aliases(node: dict[str, Any]) -> list[str]:
    aliases = node.get("aliases") or []
    names: list[str] = []
    for alias in aliases:
        name = alias.get("name") if isinstance(alias, dict) else None
        if name:
            names.append(name)
    return names


def _fallback_id(parent_tokens: list[str], depth: int) -> str:
    if parent_tokens:
        return f"{' '.join(parent_tokens)}::node-{depth}"
    return f"node-{depth}"
