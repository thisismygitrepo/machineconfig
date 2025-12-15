import ast
from pathlib import Path
from dataclasses import dataclass, field


type FieldInfo = tuple[str, ast.expr | None, dict[str, tuple[str, str]]]
type ClassFields = tuple[str, list[FieldInfo]]

_file_cache: dict[Path, ast.Module] = {}


def _get_ast(path: Path) -> ast.Module:
    if path not in _file_cache:
        _file_cache[path] = ast.parse(path.read_text(encoding="utf-8"))
    return _file_cache[path]


@dataclass
class FileContext:
    path: Path
    tree: ast.Module
    classes: dict[str, ast.ClassDef] = field(default_factory=dict)
    imports: dict[str, tuple[str, str]] = field(default_factory=dict)

    def __post_init__(self):
        self.classes = {node.name: node for node in ast.walk(self.tree) if isinstance(node, ast.ClassDef)}
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                for alias in node.names:
                    self.imports[alias.asname or alias.name] = (node.module, alias.name)


def _get_context(path: Path) -> FileContext:
    tree = _get_ast(path)
    return FileContext(path, tree)


def _resolve_imported_class(module_name: str, class_name: str, search_paths: list[Path]) -> tuple[ast.ClassDef, FileContext] | None:
    parts = module_name.split(".")
    for root in search_paths:
        file_path = root.joinpath(*parts).with_suffix(".py")
        if file_path.exists():
            try:
                context = _get_context(file_path)
                if class_name in context.classes:
                    return context.classes[class_name], context
            except Exception:
                pass
        init_path = root.joinpath(*parts, "__init__.py")
        if init_path.exists():
            try:
                context = _get_context(init_path)
                if class_name in context.classes:
                    return context.classes[class_name], context
            except Exception:
                pass
    return None


def load_target_class_fields(source_file_path: Path, search_paths: list[Path] | None = None) -> list[ClassFields]:
    source_path = Path(source_file_path).resolve()
    if search_paths is None:
        search_paths = []

    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")

    initial_context = _get_context(source_path)

    def get_parent_node(base: ast.expr, context: FileContext) -> tuple[ast.ClassDef, FileContext] | None:
        if isinstance(base, ast.Name):
            if base.id in context.classes:
                return context.classes[base.id], context
            if base.id in context.imports:
                module_name, original_name = context.imports[base.id]
                return _resolve_imported_class(module_name, original_name, search_paths)  # type: ignore
        return None

    def collect_fields(class_node: ast.ClassDef, context: FileContext, visited: set[str]) -> list[FieldInfo]:
        key = f"{context.path}:{class_node.name}"
        if key in visited:
            return []
        visited.add(key)
        field_info: list[FieldInfo] = []
        for base in class_node.bases:
            parent_info = get_parent_node(base, context)
            if parent_info:
                parent_node, parent_context = parent_info
                field_info.extend(collect_fields(parent_node, parent_context, visited))
        for statement in class_node.body:
            if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
                field_info.append((statement.target.id, statement.annotation, context.imports))
        return field_info

    def deduplicate_fields(fields: list[FieldInfo]) -> list[FieldInfo]:
        deduped: dict[str, FieldInfo] = {}
        for item in fields:
            field_name = item[0]
            deduped[field_name] = item
        return list(deduped.values())

    def is_typeddict(node: ast.ClassDef, context: FileContext, visited: set[str]) -> bool:
        key = f"{context.path}:{node.name}"
        if key in visited:
            return False
        visited.add(key)
        for base in node.bases:
            if (isinstance(base, ast.Name) and base.id == "TypedDict") or (isinstance(base, ast.Attribute) and base.attr == "TypedDict"):
                return True
            parent_info = get_parent_node(base, context)
            if parent_info:
                parent_node, parent_context = parent_info
                if is_typeddict(parent_node, parent_context, visited):
                    return True
        return False

    target_classes: list[ClassFields] = []
    for node in ast.walk(initial_context.tree):
        if not isinstance(node, ast.ClassDef):
            continue
        is_dataclass = any(
            (isinstance(decorator, ast.Name) and decorator.id == "dataclass")
            or (isinstance(decorator, ast.Attribute) and decorator.attr == "dataclass")
            or (isinstance(decorator, ast.Call) and ((isinstance(decorator.func, ast.Name) and decorator.func.id == "dataclass") or (isinstance(decorator.func, ast.Attribute) and decorator.func.attr == "dataclass")))
            for decorator in node.decorator_list
        )
        if is_dataclass or is_typeddict(node, initial_context, set()):
            fields = collect_fields(node, initial_context, set())
            target_classes.append((node.name, deduplicate_fields(fields)))
    return target_classes
