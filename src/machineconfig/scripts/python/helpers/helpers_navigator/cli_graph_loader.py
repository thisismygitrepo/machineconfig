"""
Load and normalize CLI graph data for the command navigator.
"""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from machineconfig.scripts.python.helpers.helpers_navigator.data_models import (
    CommandInfo,
    ArgumentInfo,
)


DEFAULT_CLI_GRAPH_PATH = Path(__file__).resolve().parents[2] / "graph" / "cli_graph.json"


@dataclass
class CommandNode:
    """Command info plus its children."""
    info: CommandInfo
    children: list["CommandNode"]


def load_cli_graph(path: Path | None = None) -> dict[str, Any]:
    """Load the CLI graph JSON file."""
    graph_path = path or DEFAULT_CLI_GRAPH_PATH
    with graph_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_command_nodes(graph: dict[str, Any], *, include_root: bool = False) -> list[CommandNode]:
    """Build command nodes from the CLI graph."""
    root = graph.get("root", {})
    root_name = root.get("name") if include_root else None
    parent_tokens = [root_name] if root_name else []
    children = root.get("children", [])
    return [_build_node(child, parent_tokens, parent_name=root_name) for child in children]


def _build_node(node: dict[str, Any], parent_tokens: list[str], parent_name: str | None) -> CommandNode:
    kind = node.get("kind", "command")
    name = node.get("name", "")
    tokens = parent_tokens + ([name] if name else [])
    command = " ".join(tokens).strip()
    is_group = kind == "group"
    description = _node_description(node)
    long_description = _node_long_description(node, description)
    module_path = _node_module_path(node)
    arguments = _parse_signature(node.get("signature"))
    help_text = _build_usage(command, arguments) if (command and not is_group) else ""

    info = CommandInfo(
        name=name,
        description=description,
        command=command,
        parent=parent_name,
        is_group=is_group,
        help_text=help_text,
        module_path=module_path,
        arguments=arguments,
        long_description=long_description,
    )

    children = [
        _build_node(child, tokens, parent_name=name)
        for child in node.get("children", [])
    ]
    return CommandNode(info=info, children=children)


def _node_description(node: dict[str, Any]) -> str:
    if node.get("kind") == "group":
        return (
            node.get("app", {}).get("help")
            or node.get("help")
            or node.get("doc")
            or node.get("name", "")
        )
    return (
        node.get("short_help")
        or node.get("help")
        or node.get("doc")
        or node.get("name", "")
    )


def _node_long_description(node: dict[str, Any], fallback: str) -> str:
    if node.get("kind") == "group":
        return (
            node.get("app", {}).get("help")
            or node.get("help")
            or node.get("doc")
            or fallback
        )
    return node.get("help") or node.get("doc") or fallback


def _node_module_path(node: dict[str, Any]) -> str:
    source = node.get("source") or {}
    return source.get("dispatches_to") or source.get("module") or ""


def _parse_signature(signature: dict[str, Any] | None) -> list[ArgumentInfo]:
    if not signature:
        return []

    arguments: list[ArgumentInfo] = []
    for param in signature.get("parameters", []):
        typer_info = param.get("typer") or {}
        kind = typer_info.get("kind") or ""
        name = param.get("name", "")
        is_required = bool(param.get("required", False))
        description = typer_info.get("help") or ""

        if kind == "argument":
            arguments.append(
                ArgumentInfo(
                    name=name,
                    is_required=is_required,
                    is_flag=False,
                    placeholder=name,
                    description=description,
                    is_positional=True,
                )
            )
            continue

        if kind == "option":
            flag, negated_flag = _select_flags(typer_info, name)
            long_flags = list(typer_info.get("long_flags") or [])
            short_flags = list(typer_info.get("short_flags") or [])
            is_flag = _is_bool_type(param.get("type"))
            arguments.append(
                ArgumentInfo(
                    name=name,
                    is_required=is_required,
                    is_flag=is_flag,
                    placeholder=name,
                    description=description,
                    flag=flag,
                    negated_flag=negated_flag,
                    long_flags=long_flags,
                    short_flags=short_flags,
                )
            )
            continue

    return arguments


def _is_bool_type(type_value: Any) -> bool:
    if type_value is None:
        return False
    normalized = str(type_value).replace(" ", "").lower()
    return "bool" in normalized


def _select_flags(typer_info: dict[str, Any], name: str) -> tuple[str, str]:
    long_flags = list(typer_info.get("long_flags") or [])
    short_flags = list(typer_info.get("short_flags") or [])
    param_decls = list(typer_info.get("param_decls") or [])

    candidates = long_flags or _split_param_decls(param_decls)
    if not candidates and short_flags:
        candidates = short_flags

    flag, negated_flag = _pick_positive_negative(candidates)
    if not flag:
        flag = _default_flag(name)

    return flag, negated_flag


def _split_param_decls(param_decls: list[str]) -> list[str]:
    candidates: list[str] = []
    for decl in param_decls:
        parts = [part.strip() for part in decl.split("/") if part.strip()]
        candidates.extend(parts)
    return candidates


def _pick_positive_negative(flags: list[str]) -> tuple[str, str]:
    if not flags:
        return "", ""

    positives = [flag for flag in flags if not _is_negative_flag(flag)]
    negatives = [flag for flag in flags if _is_negative_flag(flag)]

    if positives:
        return positives[0], negatives[0] if negatives else ""

    return flags[0], ""


def _is_negative_flag(flag: str) -> bool:
    token = flag.lstrip("-")
    return token.startswith("no-")


def _default_flag(name: str) -> str:
    return f"--{name.replace('_', '-')}"


def _build_usage(command: str, arguments: list[ArgumentInfo]) -> str:
    if not arguments:
        return command

    parts = [command]
    for arg in arguments:
        if arg.is_positional:
            token = f"<{arg.name}>"
            if not arg.is_required:
                token = f"[{token}]"
            parts.append(token)
            continue

        flag = arg.flag or _default_flag(arg.name)
        if arg.is_flag:
            if arg.negated_flag:
                token = f"[{flag}|{arg.negated_flag}]"
            else:
                token = f"[{flag}]"
            parts.append(token)
            continue

        placeholder = arg.placeholder or arg.name
        token = f"{flag} <{placeholder}>"
        if not arg.is_required:
            token = f"[{token}]"
        parts.append(token)

    return " ".join(parts)
