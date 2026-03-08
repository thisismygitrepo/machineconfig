from __future__ import annotations

import argparse
import ast
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence


REPO_ROOT = Path(__file__).resolve().parents[5]
SRC_ROOT = REPO_ROOT / "src"
ROOT_MODULE = "machineconfig.scripts.python.mcfg_entry"
ROOT_FACTORY = "get_app"
DEFAULT_OUTPUT_PATH = Path(__file__).resolve().with_name("cli_graph.json")


@dataclass(frozen=True)
class AppRef:
    module: str
    factory: str = "get_app"


@dataclass
class ModuleInfo:
    module: str
    path: Path
    tree: ast.Module
    source: str
    lines: list[str]
    functions: dict[str, ast.FunctionDef] = field(default_factory=dict)
    imported_modules: dict[str, str] = field(default_factory=dict)
    imported_names: dict[str, tuple[str, str]] = field(default_factory=dict)
    assignments: dict[str, ast.AST] = field(default_factory=dict)

    def relative_path(self) -> str:
        return self.path.relative_to(REPO_ROOT).as_posix()


@dataclass
class Registration:
    kind: str
    app_var: str
    target_expr: ast.AST
    order: int
    name: str | None = None
    hidden: bool = False
    help: Any = None
    short_help: Any = None
    context_settings: Any = None
    typer_config: dict[str, Any] = field(default_factory=dict)


@dataclass
class AppModel:
    ref: AppRef
    module_info: ModuleInfo
    app_var: str
    app_config: dict[str, Any]
    registrations: list[Registration]


@dataclass
class ResolvedCallable:
    module: str
    callable_name: str

    def module_ref(self) -> str:
        return f"{self.module}.{self.callable_name}"


MODULE_CACHE: dict[str, ModuleInfo] = {}
APP_CACHE: dict[AppRef, AppModel] = {}
EXPORT_CACHE: dict[tuple[str, str], Any] = {}


class Unresolved:
    def __init__(self, text: str) -> None:
        self.text = text

    def __repr__(self) -> str:
        return self.text


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate cli_graph.json from Typer source."
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"Output file path (default: {DEFAULT_OUTPUT_PATH.relative_to(REPO_ROOT)})",
    )
    args = parser.parse_args()

    payload = build_cli_graph()
    args.output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Wrote {args.output}")


def build_cli_graph() -> dict[str, Any]:
    root_ref = AppRef(module=ROOT_MODULE, factory=ROOT_FACTORY)
    root_model = load_app_model(root_ref)

    root_source = {
        "file": root_model.module_info.relative_path(),
        "module": root_ref.module,
        "app_factory": f"{root_ref.module}.{root_ref.factory}",
    }

    root_node: dict[str, Any] = {
        "kind": "root",
        "name": "mcfg",
        "help": root_model.app_config.get("help") or "MachineConfig CLI",
        "source": root_source,
        "app": root_model.app_config,
        "children": build_children(root_model),
    }

    return {
        "schema": {
            "version": "1.0",
            "description": (
                "Hierarchical CLI graph for the MachineConfig Typer-based CLI. "
                "Nodes capture command groups and leaf commands; aliases are stored "
                "on nodes rather than separate alias nodes."
            ),
            "node": {
                "kind": "root | group | command",
                "name": "CLI token for this node",
                "help": "Command help string as registered on parent (if any)",
                "short_help": "Short help string (if set)",
                "doc": "Docstring text for leaf commands or wrapper functions",
                "aliases": "List of alias objects with name/hidden/help/short_help",
                "source": "Where the callable or Typer app is defined",
                "registered_in": "Where the command was registered if different from source",
                "command_context_settings": "Typer context_settings used when registering the command",
                "app": "Typer app configuration for groups",
                "typer": "Typer command configuration for leaf commands",
                "signature": (
                    "Structured signature object for leaf commands; includes raw_lines, "
                    "parsed parameters, and return type."
                ),
                "children": "Nested subcommands",
            },
        },
        "meta": {
            "root_entrypoint": root_model.module_info.relative_path(),
            "notes": [
                "Graph derived from static source inspection of Typer app factories and lazy wrapper dispatchers.",
                "Aliases are recorded on each node with hidden flags; no standalone alias nodes.",
                "Signature objects preserve raw lines while parsing Annotated/Option/Argument metadata into structured parameters.",
            ],
        },
        "root": root_node,
    }


def build_children(app_model: AppModel) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[Registration]] = {}
    ordered_keys: list[tuple[str, str]] = []

    for reg in app_model.registrations:
        key = registration_key(reg, app_model.module_info)
        if key not in grouped:
            grouped[key] = []
            ordered_keys.append(key)
        grouped[key].append(reg)

    children: list[dict[str, Any]] = []
    for key in ordered_keys:
        regs = grouped[key]
        primary = choose_primary(regs)
        aliases = build_aliases(regs, primary)
        if key[0] == "group":
            children.append(build_group_node(app_model, primary, aliases))
        else:
            children.append(build_command_node(app_model, primary, aliases))
    return children


def registration_key(reg: Registration, module_info: ModuleInfo) -> tuple[str, str]:
    if reg.kind == "add_typer":
        child_ref = resolve_child_app_ref(reg.target_expr, module_info)
        if child_ref is None:
            name = reg.name or ast.unparse(reg.target_expr)
            return ("group", f"{module_info.module}:{name}")
        return ("group", f"{child_ref.module}.{child_ref.factory}")

    resolved = resolve_callable(reg.target_expr, module_info)
    if resolved is None:
        name = reg.name or ast.unparse(reg.target_expr)
        return ("command", f"{module_info.module}:{name}")

    dispatch_ref = find_dispatch_target(resolved)
    if dispatch_ref is not None:
        return ("group", f"{dispatch_ref.module}.{dispatch_ref.factory}")
    return ("command", resolved.module_ref())


def choose_primary(registrations: list[Registration]) -> Registration:
    visible = [reg for reg in registrations if not reg.hidden]
    return visible[0] if visible else registrations[0]


def build_aliases(
    registrations: list[Registration], primary: Registration
) -> list[dict[str, Any]]:
    aliases: list[dict[str, Any]] = []
    for reg in registrations:
        if reg is primary:
            continue
        entry: dict[str, Any] = {"name": reg.name or ""}
        if reg.hidden:
            entry["hidden"] = True
        if isinstance(reg.help, str) and reg.help:
            entry["help"] = reg.help
        if isinstance(reg.short_help, str) and reg.short_help:
            entry["short_help"] = reg.short_help
        aliases.append(entry)
    return aliases


def build_group_node(
    app_model: AppModel, reg: Registration, aliases: list[dict[str, Any]]
) -> dict[str, Any]:
    module_info = app_model.module_info
    child_ref = resolve_group_target(reg, module_info)
    if child_ref is None:
        raise RuntimeError(
            f"Could not resolve group target for {module_info.module}:{reg.name}"
        )

    child_model = load_app_model(child_ref)
    node: dict[str, Any] = {
        "kind": "group",
        "name": reg.name or "",
        "help": select_help(reg, default=child_model.app_config.get("help")),
        "source": build_group_source(app_model, reg, child_ref),
        "app": child_model.app_config,
        "children": build_children(child_model),
    }

    if reg.context_settings is not None:
        node["command_context_settings"] = reg.context_settings

    doc_value = group_doc_value(reg, module_info)
    if doc_value:
        node["doc"] = doc_value

    if aliases:
        node["aliases"] = aliases

    return node


def build_group_source(
    app_model: AppModel, reg: Registration, child_ref: AppRef
) -> dict[str, Any]:
    source: dict[str, Any] = {
        "file": app_model.module_info.relative_path(),
        "module": app_model.ref.module,
        "dispatches_to": f"{child_ref.module}.{child_ref.factory}",
    }

    if reg.kind == "command":
        resolved = resolve_callable(reg.target_expr, app_model.module_info)
        if resolved is not None:
            source["callable"] = resolved.callable_name

    return source


def group_doc_value(reg: Registration, module_info: ModuleInfo) -> str | None:
    if reg.kind != "command":
        return None
    resolved = resolve_callable(reg.target_expr, module_info)
    if resolved is None:
        return None
    function_info = load_module(resolved.module).functions.get(resolved.callable_name)
    if function_info is None:
        return None
    return ast.get_docstring(function_info)


def build_command_node(
    app_model: AppModel, reg: Registration, aliases: list[dict[str, Any]]
) -> dict[str, Any]:
    resolved = resolve_callable(reg.target_expr, app_model.module_info)
    if resolved is None:
        raise RuntimeError(
            f"Could not resolve command target for {app_model.ref.module}:{reg.name}"
        )

    function_module = load_module(resolved.module)
    function_info = function_module.functions.get(resolved.callable_name)
    if function_info is None:
        raise RuntimeError(
            f"Could not find callable {resolved.module}.{resolved.callable_name}"
        )

    doc = ast.get_docstring(function_info)
    node: dict[str, Any] = {
        "kind": "command",
        "name": reg.name or resolved.callable_name.replace("_", "-"),
        "help": select_help(reg, default=doc),
        "source": {
            "file": function_module.relative_path(),
            "module": resolved.module,
            "callable": resolved.callable_name,
        },
        "signature": build_signature(function_module, function_info),
    }

    short_help = (
        reg.short_help if isinstance(reg.short_help, str) and reg.short_help else None
    )
    if short_help is not None:
        node["short_help"] = short_help

    if reg.context_settings is not None:
        node["command_context_settings"] = reg.context_settings

    if reg.typer_config:
        node["typer"] = reg.typer_config

    if doc:
        node["doc"] = doc

    if aliases:
        node["aliases"] = aliases

    return node


def select_help(reg: Registration, default: str | None) -> str:
    if isinstance(reg.help, str) and reg.help:
        return reg.help
    if default:
        return default
    return reg.name or ""


def resolve_group_target(reg: Registration, module_info: ModuleInfo) -> AppRef | None:
    if reg.kind == "add_typer":
        return resolve_child_app_ref(reg.target_expr, module_info)

    resolved = resolve_callable(reg.target_expr, module_info)
    if resolved is None:
        return None
    return find_dispatch_target(resolved)


def find_dispatch_target(resolved: ResolvedCallable) -> AppRef | None:
    module_info = load_module(resolved.module)
    function_info = module_info.functions.get(resolved.callable_name)
    if function_info is None:
        return None

    local_modules, local_names = collect_local_imports(function_info)
    for node in ast.walk(function_info):
        if not isinstance(node, ast.Call):
            continue
        inner = node.func
        if not isinstance(inner, ast.Call):
            continue
        child_ref = resolve_child_app_ref(
            inner, module_info, local_modules=local_modules, local_names=local_names
        )
        if child_ref is not None:
            return child_ref
    return None


def resolve_child_app_ref(
    expr: ast.AST,
    module_info: ModuleInfo,
    *,
    local_modules: dict[str, str] | None = None,
    local_names: dict[str, tuple[str, str]] | None = None,
) -> AppRef | None:
    if not isinstance(expr, ast.Call):
        return None

    resolved = resolve_callable(
        expr.func, module_info, local_modules=local_modules, local_names=local_names
    )
    if resolved is None or resolved.callable_name != "get_app":
        return None
    return AppRef(module=resolved.module, factory=resolved.callable_name)


def build_signature(
    module_info: ModuleInfo, function_info: ast.FunctionDef
) -> dict[str, Any]:
    parameters = build_parameters(function_info)
    raw_lines = [
        line.rstrip("\n")
        for line in module_info.lines[
            function_info.lineno - 1 : function_info.end_lineno
        ]
    ]
    return_type = (
        ast.unparse(function_info.returns)
        if function_info.returns is not None
        else None
    )

    signature: dict[str, Any] = {
        "raw_lines": raw_lines,
        "name": function_info.name,
        "parameters": parameters,
    }
    if return_type is not None:
        signature["return"] = return_type
    return signature


def build_parameters(function_info: ast.FunctionDef) -> list[dict[str, Any]]:
    parameters: list[dict[str, Any]] = []
    args = function_info.args

    positional = list(args.posonlyargs) + list(args.args)
    positional_defaults = [None] * (len(positional) - len(args.defaults)) + list(
        args.defaults
    )

    for arg, default in zip(positional, positional_defaults, strict=True):
        parameters.append(
            build_parameter(arg=arg, default=default, kind="positional_or_keyword")
        )

    if args.vararg is not None:
        parameters.append(
            build_parameter(arg=args.vararg, default=None, kind="var_positional")
        )

    for arg, default in zip(args.kwonlyargs, args.kw_defaults, strict=True):
        parameters.append(
            build_parameter(arg=arg, default=default, kind="keyword_only")
        )

    if args.kwarg is not None:
        parameters.append(
            build_parameter(arg=args.kwarg, default=None, kind="var_keyword")
        )

    return parameters


def build_parameter(
    *, arg: ast.arg, default: ast.AST | None, kind: str
) -> dict[str, Any]:
    annotation = arg.annotation
    annotation_raw = ast.unparse(annotation) if annotation is not None else None
    param_type = extract_param_type(annotation)
    typer_info = extract_typer_info(annotation)

    entry: dict[str, Any] = {
        "name": arg.arg,
        "kind": kind,
        "type": param_type,
        "default": serialize_expr(default) if default is not None else None,
        "required": default is None,
    }

    if annotation_raw is not None:
        entry["annotation_raw"] = annotation_raw
    if typer_info is not None:
        entry["typer"] = typer_info
    return entry


def extract_param_type(annotation: ast.AST | None) -> str | None:
    if annotation is None:
        return None
    if isinstance(annotation, ast.Subscript) and is_name(annotation.value, "Annotated"):
        elements = annotation_elements(annotation)
        if elements:
            return ast.unparse(elements[0])
    return ast.unparse(annotation)


def extract_typer_info(annotation: ast.AST | None) -> dict[str, Any] | None:
    if annotation is None:
        return None
    if not (
        isinstance(annotation, ast.Subscript) and is_name(annotation.value, "Annotated")
    ):
        return None

    elements = annotation_elements(annotation)
    for metadata in elements[1:]:
        if not isinstance(metadata, ast.Call):
            continue
        func = metadata.func
        if not (isinstance(func, ast.Attribute) and is_name(func.value, "typer")):
            continue
        if func.attr not in {"Argument", "Option"}:
            continue

        default_value: str | int | float | bool | None = None
        param_decls: list[str] = []
        args = list(metadata.args)
        if args and not isinstance(args[0], ast.Constant | ast.JoinedStr):
            default_value = serialize_expr(args[0])
            args = args[1:]
        elif (
            args
            and isinstance(args[0], ast.Constant)
            and not isinstance(args[0].value, str)
        ):
            default_value = serialize_expr(args[0])
            args = args[1:]

        for value in args:
            string_value = extract_string(value)
            if string_value is not None:
                param_decls.append(string_value)

        long_flags: list[str] = []
        short_flags: list[str] = []
        for decl in param_decls:
            parts = [part.strip() for part in decl.split("/") if part.strip()]
            for part in parts:
                if part.startswith("--"):
                    long_flags.append(part)
                elif part.startswith("-"):
                    short_flags.append(part)

        entry: dict[str, Any] = {
            "kind": "argument" if func.attr == "Argument" else "option",
            "param_decls": param_decls,
            "long_flags": long_flags,
            "short_flags": short_flags,
        }
        help_value = keyword_value(metadata, "help")
        if isinstance(help_value, str):
            entry["help"] = help_value
        if default_value is not None:
            entry["default"] = default_value
        return entry
    return None


def annotation_elements(annotation: ast.Subscript) -> list[ast.AST]:
    slice_value = annotation.slice
    if isinstance(slice_value, ast.Tuple):
        return list(slice_value.elts)
    return [slice_value]


def keyword_value(call: ast.Call, name: str) -> str | None:
    for keyword in call.keywords:
        if keyword.arg == name:
            return extract_string(keyword.value)
    return None


def extract_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        parts: list[str] = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parts.append(value.value)
            else:
                return None
        return "".join(parts)
    return None


def serialize_expr(node: ast.AST | None) -> Any:
    if node is None:
        return None
    if isinstance(node, ast.Constant):
        if node.value is Ellipsis:
            return "..."
        return node.value
    if isinstance(node, ast.List):
        return [serialize_expr(elt) for elt in node.elts]
    if isinstance(node, ast.Tuple):
        return [serialize_expr(elt) for elt in node.elts]
    if isinstance(node, ast.Dict):
        result: dict[str, Any] = {}
        for key, value in zip(node.keys, node.values, strict=True):
            key_value = serialize_expr(key)
            if isinstance(key_value, str):
                result[key_value] = serialize_expr(value)
        return result
    return ast.unparse(node)


def load_app_model(ref: AppRef) -> AppModel:
    cached = APP_CACHE.get(ref)
    if cached is not None:
        return cached

    module_info = load_module(ref.module)
    function_info = module_info.functions.get(ref.factory)
    if function_info is None:
        raise RuntimeError(f"Could not find {ref.module}.{ref.factory}")

    model = extract_app_model(module_info, function_info, ref)
    APP_CACHE[ref] = model
    return model


def extract_app_model(
    module_info: ModuleInfo, function_info: ast.FunctionDef, ref: AppRef
) -> AppModel:
    env: dict[str, Any] = {}
    function_docs = {
        name: ast.get_docstring(func) for name, func in module_info.functions.items()
    }
    app_configs: dict[str, dict[str, Any]] = {}
    registrations: list[Registration] = []
    return_app_var: str | None = None
    order = 0

    def process_statements(statements: list[ast.stmt]) -> None:
        nonlocal return_app_var
        nonlocal order

        for statement in statements:
            if isinstance(statement, ast.Assign):
                value = statement.value
                for target in statement.targets:
                    if isinstance(target, ast.Name):
                        if is_typer_ctor(value):
                            app_configs[target.id] = evaluate_typer_config(
                                value, module_info, env, function_docs
                            )
                        else:
                            env[target.id] = evaluate_expr(
                                value, module_info, env, function_docs
                            )
                    elif (
                        isinstance(target, ast.Attribute)
                        and target.attr == "__doc__"
                        and isinstance(target.value, ast.Name)
                    ):
                        function_docs[target.value.id] = value_to_string(
                            evaluate_expr(value, module_info, env, function_docs),
                            fallback=ast.unparse(value),
                        )
                continue

            if isinstance(statement, ast.AnnAssign) and isinstance(
                statement.target, ast.Name
            ):
                value = statement.value
                if value is None:
                    continue
                if is_typer_ctor(value):
                    app_configs[statement.target.id] = evaluate_typer_config(
                        value, module_info, env, function_docs
                    )
                else:
                    env[statement.target.id] = evaluate_expr(
                        value, module_info, env, function_docs
                    )
                continue

            if isinstance(statement, ast.If):
                decision = evaluate_condition(
                    statement.test, module_info, env, function_docs
                )
                if decision is True:
                    process_statements(statement.body)
                elif decision is False:
                    process_statements(statement.orelse)
                else:
                    process_statements(statement.body)
                    process_statements(statement.orelse)
                continue

            if isinstance(statement, ast.Return):
                if isinstance(statement.value, ast.Name):
                    return_app_var = statement.value.id
                continue

            if isinstance(statement, ast.Expr):
                registration = parse_registration(
                    statement.value,
                    module_info=module_info,
                    env=env,
                    function_docs=function_docs,
                    order=order,
                )
                if registration is not None:
                    order += 1
                    registrations.append(registration)
                continue

    process_statements(function_info.body)

    app_var = return_app_var
    if app_var is None and app_configs:
        app_var = next(iter(app_configs))
    if app_var is None:
        raise RuntimeError(
            f"Could not identify Typer app variable in {ref.module}.{ref.factory}"
        )

    app_config = app_configs.get(app_var, {})
    return AppModel(
        ref=ref,
        module_info=module_info,
        app_var=app_var,
        app_config=app_config,
        registrations=registrations,
    )


def parse_registration(
    expr: ast.AST,
    *,
    module_info: ModuleInfo,
    env: dict[str, Any],
    function_docs: dict[str, str | None],
    order: int,
) -> Registration | None:
    if not isinstance(expr, ast.Call):
        return None

    if isinstance(expr.func, ast.Call):
        inner = expr.func
        if not isinstance(inner.func, ast.Attribute) or inner.func.attr != "command":
            return None
        if not isinstance(inner.func.value, ast.Name):
            return None
        if len(expr.args) != 1:
            return None

        app_var = inner.func.value.id
        kwargs = evaluate_kwargs(inner.keywords, module_info, env, function_docs)
        name = registration_name(inner.args, kwargs)
        typer_config = registration_typer_config(kwargs)
        return Registration(
            kind="command",
            app_var=app_var,
            target_expr=expr.args[0],
            order=order,
            name=name,
            hidden=bool(kwargs.get("hidden", False)),
            help=kwargs.get("help"),
            short_help=kwargs.get("short_help"),
            context_settings=kwargs.get("context_settings"),
            typer_config=typer_config,
        )

    if not isinstance(expr.func, ast.Attribute) or expr.func.attr != "add_typer":
        return None
    if not isinstance(expr.func.value, ast.Name):
        return None
    if not expr.args:
        return None

    app_var = expr.func.value.id
    kwargs = evaluate_kwargs(expr.keywords, module_info, env, function_docs)
    name = registration_name([], kwargs)
    return Registration(
        kind="add_typer",
        app_var=app_var,
        target_expr=expr.args[0],
        order=order,
        name=name,
        hidden=bool(kwargs.get("hidden", False)),
        help=kwargs.get("help"),
        short_help=kwargs.get("short_help"),
        context_settings=kwargs.get("context_settings"),
        typer_config=registration_typer_config(kwargs),
    )


def registration_name(args: Sequence[ast.AST], kwargs: dict[str, Any]) -> str | None:
    if "name" in kwargs and isinstance(kwargs["name"], str):
        return kwargs["name"]
    if args:
        first = args[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            return first.value
    return None


def registration_typer_config(kwargs: dict[str, Any]) -> dict[str, Any]:
    excluded = {"name", "help", "short_help", "hidden", "context_settings"}
    return {key: value for key, value in kwargs.items() if key not in excluded}


def evaluate_typer_config(
    call: ast.AST,
    module_info: ModuleInfo,
    env: dict[str, Any],
    function_docs: dict[str, str | None],
) -> dict[str, Any]:
    if not isinstance(call, ast.Call):
        return {}
    return evaluate_kwargs(call.keywords, module_info, env, function_docs)


def evaluate_kwargs(
    keywords: list[ast.keyword],
    module_info: ModuleInfo,
    env: dict[str, Any],
    function_docs: dict[str, str | None],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for keyword in keywords:
        if keyword.arg is None:
            continue
        result[keyword.arg] = simplify_value(
            evaluate_expr(keyword.value, module_info, env, function_docs),
            fallback=ast.unparse(keyword.value),
        )
    return result


def evaluate_condition(
    expr: ast.AST,
    module_info: ModuleInfo,
    env: dict[str, Any],
    function_docs: dict[str, str | None],
) -> bool | None:
    value = evaluate_expr(expr, module_info, env, function_docs)
    if isinstance(value, Unresolved):
        return None
    if isinstance(value, bool):
        return value
    return None


def evaluate_expr(
    expr: ast.AST,
    module_info: ModuleInfo,
    env: dict[str, Any],
    function_docs: dict[str, str | None],
) -> Any:
    if isinstance(expr, ast.Constant):
        return expr.value

    if isinstance(expr, ast.Name):
        if expr.id in env:
            return env[expr.id]
        if expr.id in function_docs:
            return {"__doc__": function_docs[expr.id] or ""}
        imported = resolve_imported_symbol(module_info, expr.id)
        if imported is not None:
            return imported
        return Unresolved(expr.id)

    if isinstance(expr, ast.JoinedStr):
        parts: list[str] = []
        for value in expr.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parts.append(value.value)
                continue
            if isinstance(value, ast.FormattedValue):
                formatted = evaluate_expr(value.value, module_info, env, function_docs)
                if isinstance(formatted, Unresolved):
                    return Unresolved(ast.unparse(expr))
                parts.append(str(formatted))
                continue
            return Unresolved(ast.unparse(expr))
        return "".join(parts)

    if isinstance(expr, ast.List):
        return [
            simplify_value(
                evaluate_expr(item, module_info, env, function_docs),
                fallback=ast.unparse(item),
            )
            for item in expr.elts
        ]

    if isinstance(expr, ast.Tuple):
        return tuple(
            simplify_value(
                evaluate_expr(item, module_info, env, function_docs),
                fallback=ast.unparse(item),
            )
            for item in expr.elts
        )

    if isinstance(expr, ast.Dict):
        result: dict[str, Any] = {}
        for key, value in zip(expr.keys, expr.values, strict=True):
            if key is None:
                return Unresolved(ast.unparse(expr))
            key_value = evaluate_expr(key, module_info, env, function_docs)
            if isinstance(key_value, Unresolved) or not isinstance(key_value, str):
                return Unresolved(ast.unparse(expr))
            result[key_value] = simplify_value(
                evaluate_expr(value, module_info, env, function_docs),
                fallback=ast.unparse(value),
            )
        return result

    if isinstance(expr, ast.Attribute):
        base = evaluate_expr(expr.value, module_info, env, function_docs)
        if expr.attr == "__doc__" and isinstance(base, dict):
            return base.get("__doc__", "")
        return Unresolved(ast.unparse(expr))

    if isinstance(expr, ast.Subscript):
        base = evaluate_expr(expr.value, module_info, env, function_docs)
        key = evaluate_expr(expr.slice, module_info, env, function_docs)
        if isinstance(base, Unresolved) or isinstance(key, Unresolved):
            return Unresolved(ast.unparse(expr))
        try:
            return base[key]
        except Exception:
            return Unresolved(ast.unparse(expr))

    if isinstance(expr, ast.UnaryOp) and isinstance(expr.op, ast.Not):
        value = evaluate_expr(expr.operand, module_info, env, function_docs)
        if isinstance(value, Unresolved):
            return value
        return not bool(value)

    if isinstance(expr, ast.BoolOp):
        values = [
            evaluate_expr(value, module_info, env, function_docs)
            for value in expr.values
        ]
        if any(isinstance(value, Unresolved) for value in values):
            return Unresolved(ast.unparse(expr))
        if isinstance(expr.op, ast.And):
            return all(bool(value) for value in values)
        if isinstance(expr.op, ast.Or):
            return any(bool(value) for value in values)

    if (
        isinstance(expr, ast.Compare)
        and len(expr.ops) == 1
        and len(expr.comparators) == 1
    ):
        left = evaluate_expr(expr.left, module_info, env, function_docs)
        right = evaluate_expr(expr.comparators[0], module_info, env, function_docs)
        if isinstance(left, Unresolved) or isinstance(right, Unresolved):
            return Unresolved(ast.unparse(expr))
        op = expr.ops[0]
        if isinstance(op, ast.Eq):
            return left == right
        if isinstance(op, ast.NotEq):
            return left != right

    if isinstance(expr, ast.Call):
        return evaluate_call(expr, module_info, env, function_docs)

    if isinstance(expr, ast.Subscript) and is_name(expr.value, "Literal"):
        values = literal_values(expr)
        return tuple(values)

    return Unresolved(ast.unparse(expr))


def evaluate_call(
    expr: ast.Call,
    module_info: ModuleInfo,
    env: dict[str, Any],
    function_docs: dict[str, str | None],
) -> Any:
    if is_name(expr.func, "get_args") and len(expr.args) == 1:
        value = evaluate_expr(expr.args[0], module_info, env, function_docs)
        if isinstance(value, Unresolved):
            return value
        if isinstance(value, tuple):
            return value
        if isinstance(value, list):
            return tuple(value)
        return Unresolved(ast.unparse(expr))

    if (
        isinstance(expr.func, ast.Attribute)
        and expr.func.attr == "join"
        and len(expr.args) == 1
    ):
        base = evaluate_expr(expr.func.value, module_info, env, function_docs)
        value = evaluate_expr(expr.args[0], module_info, env, function_docs)
        if isinstance(base, str) and not isinstance(value, Unresolved):
            if isinstance(value, tuple):
                return base.join(str(item) for item in value)
            if isinstance(value, list):
                return base.join(str(item) for item in value)
        return Unresolved(ast.unparse(expr))

    if (
        isinstance(expr.func, ast.Attribute)
        and expr.func.attr == "home"
        and is_name(expr.func.value, "Path")
    ):
        if expr.args or expr.keywords:
            return Unresolved(ast.unparse(expr))
        return Path.home()

    if isinstance(expr.func, ast.Attribute) and expr.func.attr == "joinpath":
        base = evaluate_expr(expr.func.value, module_info, env, function_docs)
        if isinstance(base, Path):
            args: list[str] = []
            for arg in expr.args:
                value = evaluate_expr(arg, module_info, env, function_docs)
                if isinstance(value, Unresolved):
                    return value
                args.append(str(value))
            return base.joinpath(*args)
        return Unresolved(ast.unparse(expr))

    if isinstance(expr.func, ast.Attribute) and expr.func.attr == "exists":
        base = evaluate_expr(expr.func.value, module_info, env, function_docs)
        if isinstance(base, Path) and not expr.args and not expr.keywords:
            return base.exists()
        return Unresolved(ast.unparse(expr))

    return Unresolved(ast.unparse(expr))


def resolve_imported_symbol(module_info: ModuleInfo, name: str) -> Any | None:
    if name in module_info.imported_names:
        module, attr = module_info.imported_names[name]
        if module == "pathlib" and attr == "Path":
            return Path
        if module == "typing" and attr == "get_args":
            return "get_args"
        return resolve_exported_value(module, attr)
    return None


def resolve_exported_value(module: str, attr: str) -> Any | None:
    cache_key = (module, attr)
    if cache_key in EXPORT_CACHE:
        return EXPORT_CACHE[cache_key]

    try:
        module_info = load_module(module)
    except FileNotFoundError:
        EXPORT_CACHE[cache_key] = None
        return None

    if attr in module_info.assignments:
        value = evaluate_module_assignment(module_info, module_info.assignments[attr])
        EXPORT_CACHE[cache_key] = value
        return value

    if attr in module_info.imported_names:
        imported_module, imported_attr = module_info.imported_names[attr]
        value = resolve_exported_value(imported_module, imported_attr)
        EXPORT_CACHE[cache_key] = value
        return value

    EXPORT_CACHE[cache_key] = None
    return None


def evaluate_module_assignment(module_info: ModuleInfo, expr: ast.AST) -> Any:
    if isinstance(expr, ast.Constant):
        return expr.value
    if isinstance(expr, ast.Subscript) and is_name(expr.value, "Literal"):
        return tuple(literal_values(expr))
    return None


def literal_values(expr: ast.Subscript) -> list[Any]:
    slice_value = expr.slice
    values = (
        list(slice_value.elts) if isinstance(slice_value, ast.Tuple) else [slice_value]
    )
    result: list[Any] = []
    for value in values:
        if isinstance(value, ast.Constant):
            result.append(value.value)
        else:
            result.append(ast.unparse(value))
    return result


def simplify_value(value: Any, *, fallback: str) -> Any:
    if isinstance(value, Unresolved):
        return value.text
    if isinstance(value, tuple):
        return [simplify_value(item, fallback=str(item)) for item in value]
    if isinstance(value, list):
        return [simplify_value(item, fallback=str(item)) for item in value]
    if isinstance(value, dict):
        simplified: dict[str, Any] = {}
        for key, item in value.items():
            simplified[str(key)] = simplify_value(item, fallback=str(item))
        return simplified
    return value if value is not None else fallback if fallback == "None" else value


def value_to_string(value: Any, *, fallback: str) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, Unresolved):
        return value.text
    return fallback


def load_module(module: str) -> ModuleInfo:
    cached = MODULE_CACHE.get(module)
    if cached is not None:
        return cached

    path = module_to_path(module)
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    info = ModuleInfo(module=module, path=path, tree=tree, source=source, lines=lines)

    for statement in tree.body:
        if isinstance(statement, ast.FunctionDef):
            info.functions[statement.name] = statement
        elif isinstance(statement, ast.Import):
            for alias in statement.names:
                local = alias.asname or alias.name
                info.imported_modules[local] = alias.name
        elif isinstance(statement, ast.ImportFrom) and statement.module is not None:
            for alias in statement.names:
                local = alias.asname or alias.name
                info.imported_names[local] = (statement.module, alias.name)
        elif isinstance(statement, ast.Assign):
            for target in statement.targets:
                if isinstance(target, ast.Name):
                    info.assignments[target.id] = statement.value
        elif (
            isinstance(statement, ast.AnnAssign)
            and isinstance(statement.target, ast.Name)
            and statement.value is not None
        ):
            info.assignments[statement.target.id] = statement.value

    MODULE_CACHE[module] = info
    return info


def module_to_path(module: str) -> Path:
    parts = module.split(".")
    direct = SRC_ROOT.joinpath(*parts).with_suffix(".py")
    if direct.exists():
        return direct
    package = SRC_ROOT.joinpath(*parts, "__init__.py")
    if package.exists():
        return package
    raise FileNotFoundError(f"Could not resolve module path for {module}")


def resolve_callable(
    expr: ast.AST,
    module_info: ModuleInfo,
    *,
    local_modules: dict[str, str] | None = None,
    local_names: dict[str, tuple[str, str]] | None = None,
) -> ResolvedCallable | None:
    dotted = dotted_name(expr)
    if dotted is None:
        return None

    parts = dotted.split(".")
    root = parts[0]
    imported_modules = dict(module_info.imported_modules)
    imported_names = dict(module_info.imported_names)
    if local_modules:
        imported_modules.update(local_modules)
    if local_names:
        imported_names.update(local_names)

    if root in module_info.functions and len(parts) == 1:
        return ResolvedCallable(module=module_info.module, callable_name=root)

    if root in imported_names:
        imported_module, imported_attr = imported_names[root]
        full = ".".join([imported_module, imported_attr, *parts[1:]])
        split = split_module_and_callable(full)
        if split is not None:
            return ResolvedCallable(module=split[0], callable_name=split[1])

    if root in imported_modules:
        full = ".".join([imported_modules[root], *parts[1:]])
        split = split_module_and_callable(full)
        if split is not None:
            return ResolvedCallable(module=split[0], callable_name=split[1])

    if root == "machineconfig":
        split = split_module_and_callable(dotted)
        if split is not None:
            return ResolvedCallable(module=split[0], callable_name=split[1])

    return None


def split_module_and_callable(reference: str) -> tuple[str, str] | None:
    parts = reference.split(".")
    for index in range(len(parts) - 1, 0, -1):
        module = ".".join(parts[:index])
        callable_name = parts[index]
        try:
            module_to_path(module)
        except FileNotFoundError:
            continue
        return module, callable_name
    return None


def dotted_name(expr: ast.AST) -> str | None:
    if isinstance(expr, ast.Name):
        return expr.id
    if isinstance(expr, ast.Attribute):
        parent = dotted_name(expr.value)
        if parent is None:
            return None
        return f"{parent}.{expr.attr}"
    return None


def collect_local_imports(
    function_info: ast.FunctionDef,
) -> tuple[dict[str, str], dict[str, tuple[str, str]]]:
    imported_modules: dict[str, str] = {}
    imported_names: dict[str, tuple[str, str]] = {}

    for node in ast.walk(function_info):
        if isinstance(node, ast.Import):
            for alias in node.names:
                local = alias.asname or alias.name
                imported_modules[local] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            for alias in node.names:
                local = alias.asname or alias.name
                imported_names[local] = (node.module, alias.name)

    return imported_modules, imported_names


def is_typer_ctor(expr: ast.AST) -> bool:
    return (
        isinstance(expr, ast.Call)
        and isinstance(expr.func, ast.Attribute)
        and expr.func.attr == "Typer"
        and is_name(expr.func.value, "typer")
    )


def is_name(expr: ast.AST, name: str) -> bool:
    return isinstance(expr, ast.Name) and expr.id == name


if __name__ == "__main__":
    main()
