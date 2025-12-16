import ast
import inspect
from pathlib import Path
from typing import Literal


WRAPPER_TYPES = {"ReadOnly", "NotRequired", "Optional", "Required", "Final"}
BUILTIN_TYPES = {"str", "int", "float", "bool", "bytes", "None", "list", "dict", "set", "tuple", "Any", "Literal"}
PYTHON_TYPE_TO_SERIES_TYPE: dict[str, str] = {"str": "str", "int": "int", "float": "float", "bool": "bool", "bytes": "bytes"}
PYTHON_TYPE_TO_POLARS_DTYPE: dict[str, str] = {"str": '"pl.String"', "int": '"pl.Int64"', "float": '"pl.Float64"', "bool": '"pl.Boolean"', "bytes": '"pl.Binary"'}


def get_types_class_name(class_name: str) -> str:
    return f"{class_name}_Types"


def collect_type_names_from_annotation(annotation: ast.expr | None) -> set[str]:
    if annotation is None:
        return set()
    names: set[str] = set()
    if isinstance(annotation, ast.Name):
        if annotation.id not in BUILTIN_TYPES and annotation.id not in WRAPPER_TYPES:
            names.add(annotation.id)
    elif isinstance(annotation, ast.Subscript):
        names.update(collect_type_names_from_annotation(annotation.value))
        names.update(collect_type_names_from_annotation(annotation.slice))
    elif isinstance(annotation, ast.BinOp):
        names.update(collect_type_names_from_annotation(annotation.left))
        names.update(collect_type_names_from_annotation(annotation.right))
    elif isinstance(annotation, ast.Tuple):
        for elt in annotation.elts:
            names.update(collect_type_names_from_annotation(elt))
    return names


def extract_imports_from_source(source_file_path: Path) -> tuple[dict[str, str], dict[str, str], set[str]]:
    source_content = source_file_path.read_text(encoding="utf-8")
    tree = ast.parse(source_content)
    imports: dict[str, str] = {}
    local_type_aliases: dict[str, str] = {}
    local_classes: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                name = alias.asname or alias.name
                imports[name] = node.module
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if isinstance(node.annotation, ast.Name) and node.annotation.id == "TypeAlias" and node.value is not None:
                local_type_aliases[node.target.id] = ast.unparse(node.value)
        elif isinstance(node, ast.ClassDef):
            local_classes.add(node.name)
    return imports, local_type_aliases, local_classes


def unwrap_type_annotation(annotation: ast.expr | None) -> ast.expr | None:
    if annotation is None:
        return None
    if isinstance(annotation, ast.Subscript) and isinstance(annotation.value, ast.Name) and annotation.value.id in WRAPPER_TYPES:
        return unwrap_type_annotation(annotation.slice)
    if isinstance(annotation, ast.Subscript) and isinstance(annotation.value, ast.Attribute) and annotation.value.attr in WRAPPER_TYPES:
        return unwrap_type_annotation(annotation.slice)
    return annotation


def is_builtin_type(annotation: ast.expr) -> bool:
    if isinstance(annotation, ast.Name):
        return annotation.id in BUILTIN_TYPES
    if isinstance(annotation, ast.Constant):
        return True
    if isinstance(annotation, ast.Subscript):
        return is_builtin_type(annotation.value) and is_builtin_type(annotation.slice)
    if isinstance(annotation, ast.Attribute):
        return False
    if isinstance(annotation, ast.BinOp):
        return is_builtin_type(annotation.left) and is_builtin_type(annotation.right)
    if isinstance(annotation, ast.Tuple):
        return all(is_builtin_type(elt) for elt in annotation.elts)
    return False


def python_type_to_iterable_str(annotation: ast.expr | None) -> str:
    unwrapped = unwrap_type_annotation(annotation)
    if unwrapped is None:
        return 'Iterable["Any"]'
    type_str = ast.unparse(unwrapped)
    if not is_builtin_type(unwrapped):
        return f'Iterable["{type_str}"]'
    return f"Iterable[{type_str}]"


def get_iterable_type_for_col(annotation: ast.expr | None) -> str:
    unwrapped = unwrap_type_annotation(annotation)
    if unwrapped is None:
        return 'Annotated["pl.Series", Any]'
    if isinstance(unwrapped, ast.Name):
        dtype = PYTHON_TYPE_TO_POLARS_DTYPE.get(unwrapped.id)
        if dtype:
            return f'Annotated["pl.Series", {dtype}]'
        return 'Annotated["pl.Series", Any]'
    if isinstance(unwrapped, ast.Subscript) and isinstance(unwrapped.value, ast.Name):
        if unwrapped.value.id == "list":
            return 'Annotated["pl.Series", "pl.List"]'
    return 'Annotated["pl.Series", Any]'


def get_random_value_expr(annotation: ast.expr | None) -> str:
    unwrapped = unwrap_type_annotation(annotation)
    if unwrapped is None:
        return "None"
    if isinstance(unwrapped, ast.Name):
        type_name = unwrapped.id
        if type_name == "str":
            return "pl.Series([secrets.token_hex(8) for _ in range(n_rows)])"
        if type_name == "int":
            return "pl.Series(random.choices(range(-1000, 1000), k=n_rows))"
        if type_name == "float":
            return "pl.Series([random.uniform(-1000.0, 1000.0) for _ in range(n_rows)])"
        if type_name == "bool":
            return "pl.Series(random.choices([True, False], k=n_rows))"
        if type_name == "bytes":
            return "pl.Series([secrets.token_bytes(16) for _ in range(n_rows)])"
        return "pl.Series([None] * n_rows)"
    if isinstance(unwrapped, ast.Subscript) and isinstance(unwrapped.value, ast.Name):
        if unwrapped.value.id == "list":
            return "pl.Series([[random.randint(0, 100) for _ in range(3)] for _ in range(n_rows)])"
    return "pl.Series([None] * n_rows)"


# def _check_random_imports_needed(field_infos: list[tuple[str, ast.expr | None]]) -> tuple[bool, bool]:
#     needs_random = False
#     needs_secrets = False
#     for _field_name, annotation in field_infos:
#         unwrapped = unwrap_type_annotation(annotation)
#         if unwrapped is None:
#             continue
#         if isinstance(unwrapped, ast.Name):
#             type_name = unwrapped.id
#             if type_name in {"int", "float", "bool"}:
#                 needs_random = True
#             elif type_name in {"str", "bytes"}:
#                 needs_secrets = True
#         elif isinstance(unwrapped, ast.Subscript) and isinstance(unwrapped.value, ast.Name):
#             if unwrapped.value.id == "list":
#                 needs_random = True
#     return needs_random, needs_secrets


def quote_pl_in_annotation(annotation_str: str) -> str:
    """Quote pl.X types in annotation strings since pl is only available under TYPE_CHECKING."""
    import re
    # Match pl.X only when NOT already inside quotes (preceded by ' or ")
    # Use negative lookbehind for quotes
    return re.sub(r"(?<!['\"])(\bpl\.\w+)(?!['\"])", r"'\1'", annotation_str)


def _get_module_name_from_output_path(file_path: Path) -> str:
    """Get the module name from the output file path."""
    resolved = file_path.resolve()
    parts: list[str] = []
    current = resolved.parent
    while current != current.parent:
        if not (current / "__init__.py").exists():
            break
        parts.append(current.name)
        current = current.parent
    parts.reverse()
    return ".".join(parts) if parts else ""


def get_module_level_helper_functions() -> list[str]:
    """Get helper functions to be defined once at module level for self-contained mode.
    Returns only the function definitions, not imports (imports are handled separately at file top).
    """
    from machineconfig.type_hinting import polars_schema_typeddict
    
    lines = []
    lines.append("# Helper functions for self-contained mode (defined once at module level)")
    lines.append("")
    
    # Add all helper functions
    for func_name in ["_unwrap_type", "_get_polars_type", "get_polars_schema_from_typeddict", "get_polars_df_random_data_from_typeddict"]:
        func = getattr(polars_schema_typeddict, func_name)
        source = inspect.getsource(func)
        for line in source.splitlines():
            lines.append(line)
        lines.append("")
    
    return lines


def generate_for_class(class_name: str, field_infos: list[tuple[str, ast.expr | None]], source_module: str, dependency: Literal["import", "self-contained"] = "self-contained", output_file_path: Path | None = None) -> list[str]:
    lines: list[str] = []
    field_names = [fn for fn, _ in field_infos]

    types_class_name = get_types_class_name(class_name)

    names_class_name = f"{class_name}Names"
    lines.append(f"class {names_class_name}:")
    if field_infos:
        for field_name in field_names:
            lines.append(f'    {field_name}: Literal["{field_name}"] = "{field_name}"')
    else:
        lines.append("    pass")
    lines.append("")
    lines.append("")

    names_literal = f"{class_name}_NAMES"
    if field_names:
        literal_values = ", ".join(f'"{fn}"' for fn in field_names)
        lines.append(f'{names_literal}: TypeAlias = Literal[{literal_values}]')
    else:
        lines.append(f'{names_literal}: TypeAlias = Literal[""]')
    lines.append("")
    lines.append("")

    lines.append(f"class {types_class_name}:")
    if field_infos:
        for field_name, annotation in field_infos:
            if annotation is None:
                raise ValueError(f"Field '{field_name}' in class '{class_name}' lacks an annotation")
            unwrapped = unwrap_type_annotation(annotation)
            if unwrapped is None:
                raise ValueError(f"Field '{field_name}' in class '{class_name}' lacks an annotation")
            annotation_source = ast.unparse(unwrapped)
            annotation_source = quote_pl_in_annotation(annotation_source)
            lines.append(f"    {field_name}: TypeAlias = {annotation_source}")
    else:
        lines.append("    pass")
    lines.append("")
    lines.append("")

    wrapper_class_name = f"{class_name}_Wrapper"
    lines.append(f"class {wrapper_class_name}:")
    lines.append(f"    c = {names_class_name}")
    lines.append(f"    ct: TypeAlias = {names_literal}")
    lines.append(f'    e: TypeAlias = {class_name}')
    lines.append(f"    t: TypeAlias = {types_class_name}")
    lines.append("")
    lines.append('    def __init__(self, df: "pl.DataFrame") -> None:')
    lines.append("        self.df = df")
    lines.append("")

    if field_infos:
        # Group fields by their return type to reduce number of overloads
        grouped_fields: dict[str, list[str]] = {}
        for field_name, annotation in field_infos:
            col_type = get_iterable_type_for_col(annotation)
            grouped_fields.setdefault(col_type, []).append(field_name)

        if len(grouped_fields) == 1:
            col_type = list(grouped_fields.keys())[0]
            lines.append(f'    def get_col(self, name: {names_literal}) -> {col_type}:')
            lines.append("        return self.df.select(name).to_series()")
            lines.append("")
        else:
            for col_type, fields in grouped_fields.items():
                lines.append("    @overload")
                if len(fields) == 1:
                    lines.append(f'    def get_col(self, name: Literal["{fields[0]}"]) -> {col_type}: ...')
                else:
                    literals = ", ".join(f'"{f}"' for f in fields)
                    lines.append(f'    def get_col(self, name: Literal[{literals}]) -> {col_type}: ...')

            lines.append(f'    def get_col(self, name: {names_literal}) -> Annotated["pl.Series", Any]:')
            lines.append("        return self.df.select(name).to_series()")
            lines.append("")

        params: list[str] = []
        dict_entries: list[str] = []
        for field_name, annotation in field_infos:
            iterable_type = python_type_to_iterable_str(annotation)
            params.append(f"{field_name}: {iterable_type}")
            dict_entries.append(f'"{field_name}": {field_name}')
        params_str = ", ".join(params)
        dict_str = "{" + ", ".join(dict_entries) + "}"
        lines.append("    @staticmethod")
        lines.append(f'    def make({params_str}) -> "{wrapper_class_name}":')
        
        if dependency == "import":
            # Use fully qualified import from dtypes_utils
            if output_file_path:
                output_module = _get_module_name_from_output_path(output_file_path)
                lines.append(f"        from {output_module}.dtypes_utils import get_polars_schema_from_typeddict as get_polars_schema")
            else:
                lines.append("        from machineconfig.type_hinting.polars_schema_typeddict import get_polars_schema_from_typeddict as get_polars_schema")
        else:  # self-contained - use module-level function
            lines.append("        get_polars_schema = get_polars_schema_from_typeddict")
        
        lines.append(f"        return {wrapper_class_name}(pl.DataFrame({dict_str}, schema=get_polars_schema({class_name})))")
        lines.append("")

        lines.append("    @staticmethod")
        lines.append(f'    def make_fake(n_rows: int) -> "{wrapper_class_name}":')
        
        if dependency == "import":
            # Use fully qualified import from dtypes_utils
            if output_file_path:
                output_module = _get_module_name_from_output_path(output_file_path)
                lines.append(f"        from {output_module}.dtypes_utils import get_polars_df_random_data_from_typeddict")
            else:
                lines.append("        from machineconfig.type_hinting.polars_schema_typeddict import get_polars_df_random_data_from_typeddict")
        else:  # self-contained - use module-level function
            pass  # No imports needed, function is at module level
        
        lines.append(f"        return {wrapper_class_name}(get_polars_df_random_data_from_typeddict({class_name}, n_rows))")
    else:
        lines.append("    @staticmethod")
        lines.append(f'    def make() -> "{wrapper_class_name}":')
        lines.append("        import polars as pl")
        lines.append(f"        return {wrapper_class_name}(pl.DataFrame())")
        lines.append("")
        lines.append("    @staticmethod")
        lines.append(f'    def make_fake(n_rows: int) -> "{wrapper_class_name}":')
        lines.append("        import polars as pl")
        lines.append("        _ = n_rows")
        lines.append(f"        return {wrapper_class_name}(pl.DataFrame())")
    lines.append("")
    lines.append("")
    return lines
