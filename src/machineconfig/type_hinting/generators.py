import ast
import shutil
from pathlib import Path
from typing import Literal

from machineconfig.type_hinting.ast_utils import load_target_class_fields
from machineconfig.type_hinting.generator_helpers import (
    collect_type_names_from_annotation,
    extract_imports_from_source,
    generate_for_class,
    get_types_class_name,
    unwrap_type_annotation,
)


def _get_module_name_from_path(file_path: Path) -> str:
    resolved = file_path.resolve()
    parts: list[str] = [resolved.stem]
    current = resolved.parent
    while current != current.parent:
        if not (current / "__init__.py").exists():
            break
        parts.append(current.name)
        current = current.parent
    parts.reverse()
    return ".".join(parts)


def generate_names_file(source_file_path: Path, output_file_path: Path, search_paths: list[Path] | None = None, dependency: Literal["import", "self-contained"] = "self-contained") -> Path:
    target_classes = load_target_class_fields(source_file_path, search_paths)
    target_path = Path(output_file_path).resolve()
    
    # Handle dependency mode: copy dtypes_utils.py for 'import' mode
    if dependency == "import":
        source_polars_schema = Path(__file__).parent / "polars_schema_typeddict.py"
        target_dtypes_utils = target_path.parent / "dtypes_utils.py"
        shutil.copy2(source_polars_schema, target_dtypes_utils)

    source_imports, local_type_aliases, local_classes = extract_imports_from_source(Path(source_file_path))

    all_custom_types: dict[str, str | None] = {}
    for _class_name, field_infos in target_classes:
        for _field_name, annotation, field_imports in field_infos:
            unwrapped = unwrap_type_annotation(annotation)
            type_names = collect_type_names_from_annotation(unwrapped)
            for type_name in type_names:
                if type_name not in all_custom_types:
                    if type_name in field_imports:
                        all_custom_types[type_name] = field_imports[type_name][0]
                    else:
                        all_custom_types[type_name] = None

    grouped_imports: dict[str, list[str]] = {}
    needed_local_aliases: list[str] = []
    needed_local_classes: list[str] = []
    for type_name in sorted(all_custom_types.keys()):
        module = all_custom_types[type_name]
        if module:
            grouped_imports.setdefault(module, []).append(type_name)
        elif type_name in source_imports:
            module = source_imports[type_name]
            grouped_imports.setdefault(module, []).append(type_name)
        elif type_name in local_type_aliases:
            needed_local_aliases.append(type_name)
        elif type_name in local_classes:
            needed_local_classes.append(type_name)
    
    # Check if Any is actually used in get_col return type annotations
    uses_any = False
    for _class_name, field_infos in target_classes:
        if not field_infos:  # Empty class won't have get_col with Any
            continue
        # Check if there are multiple different column types (which means we need Any fallback)
        from machineconfig.type_hinting.generator_helpers import get_iterable_type_for_col
        col_types = set()
        for _field_name, annotation in [(fn, ann) for fn, ann, _ in field_infos]:
            col_types.add(get_iterable_type_for_col(annotation))
        if len(col_types) > 1:
            uses_any = True
            break

    # Build typing imports based on what's needed
    typing_imports = ["Annotated", "Literal", "TypeAlias", "TYPE_CHECKING", "overload"]
    if uses_any:
        typing_imports.insert(1, "Any")  # Insert after Annotated
    
    lines: list[str] = ["from collections.abc import Iterable", f"from typing import {', '.join(typing_imports)}"]
    
    # Add self-contained mode imports right at the top
    if dependency == "self-contained":
        lines.append("from typing import ReadOnly, get_origin, get_args")
        lines.append("import polars as pl")
        lines.append("import random")
        lines.append("import secrets")
    
    lines.append("")

    target_class_names = [class_name for class_name, _ in target_classes]
    source_module = _get_module_name_from_path(source_file_path)
    if target_class_names:
        lines.append(f"from {source_module} import {', '.join(sorted(target_class_names))}")

    for alias_name in sorted(needed_local_aliases):
        lines.append(f"{alias_name}: TypeAlias = {local_type_aliases[alias_name]}")
    if needed_local_aliases:
        lines.append("")

    # Runtime imports: types used in _Types classes (TypeAlias assignments) need to be available at runtime
    for module, type_names in sorted(grouped_imports.items()):
        lines.append(f"from {module} import {', '.join(sorted(type_names))}")
    
    # Check if numpy (np) is used in type aliases - look through all annotations
    needs_numpy = False
    for _class_name, field_infos in target_classes:
        for _field_name, annotation, _field_imports in field_infos:
            if annotation:
                import ast
                annotation_str = ast.unparse(annotation)
                if 'np.' in annotation_str:
                    needs_numpy = True
                    break
        if needs_numpy:
            break
    
    if needs_numpy:
        lines.append("import numpy as np")

    lines.append("")
    # Only add TYPE_CHECKING block for non-self-contained mode (self-contained imports polars at top)
    if dependency != "self-contained":
        lines.append("if TYPE_CHECKING:")
        lines.append("    import polars as pl")
    else:
        # For self-contained, polars is already imported at the top
        lines.append("if TYPE_CHECKING:")
        lines.append("    pass")
    all_type_checking_imports = sorted(set(needed_local_classes) - set(target_class_names))
    if all_type_checking_imports:
        lines.append(f"    from {source_module} import {', '.join(all_type_checking_imports)}")
    lines.append("")
    
    # For self-contained mode, add helper functions at module level
    if dependency == "self-contained":
        from machineconfig.type_hinting.generator_helpers import get_module_level_helper_functions
        helper_lines = get_module_level_helper_functions()
        lines.extend(helper_lines)
        lines.append("")

    for class_name, field_infos in target_classes:
        source_module = _get_module_name_from_path(source_file_path)
        stripped_field_infos = [(fn, ann) for fn, ann, _ in field_infos]
        lines.extend(generate_for_class(class_name, stripped_field_infos, source_module, dependency=dependency, output_file_path=target_path))

    lines.append("")
    lines.append('if __name__ == "__main__":')
    lines.append("    import polars as pl")
    lines.append("")

    output_content = "\n".join(lines)
    with target_path.open(mode="w", encoding="utf-8") as f:
        f.write(output_content)
    return target_path


def generate_types_file(source_file_path: Path, output_file_path: Path, search_paths: list[Path] | None = None) -> Path:
    target_classes = load_target_class_fields(source_file_path, search_paths)
    target_path = Path(output_file_path).resolve()

    source_imports, local_type_aliases, local_classes = extract_imports_from_source(Path(source_file_path))

    all_custom_types: dict[str, str | None] = {}
    for _class_name, field_infos in target_classes:
        for _field_name, annotation, field_imports in field_infos:
            unwrapped = unwrap_type_annotation(annotation)
            type_names = collect_type_names_from_annotation(unwrapped)
            for type_name in type_names:
                if type_name not in all_custom_types:
                    if type_name in field_imports:
                        all_custom_types[type_name] = field_imports[type_name][0]
                    else:
                        all_custom_types[type_name] = None

    grouped_imports: dict[str, list[str]] = {}
    needed_local_aliases: list[str] = []
    needed_local_classes: list[str] = []
    for type_name in sorted(all_custom_types.keys()):
        module = all_custom_types[type_name]
        if module:
            grouped_imports.setdefault(module, []).append(type_name)
        elif type_name in source_imports:
            module = source_imports[type_name]
            grouped_imports.setdefault(module, []).append(type_name)
        elif type_name in local_type_aliases:
            needed_local_aliases.append(type_name)
        elif type_name in local_classes:
            needed_local_classes.append(type_name)

    lines: list[str] = ["from typing import TypeAlias"]
    for module, type_names in sorted(grouped_imports.items()):
        lines.append(f"from {module} import {', '.join(sorted(type_names))}")
    if needed_local_classes:
        source_module = _get_module_name_from_path(source_file_path)
        lines.append(f"from {source_module} import {', '.join(sorted(needed_local_classes))}")
    lines.append("")
    for alias_name in sorted(needed_local_aliases):
        lines.append(f"{alias_name}: TypeAlias = {local_type_aliases[alias_name]}")
    if needed_local_aliases:
        lines.append("")
    lines.append("")

    for class_name, field_infos in target_classes:
        types_class_name = get_types_class_name(class_name)
        lines.append(f"class {types_class_name}:")
        if field_infos:
            for field_name, annotation, _ in field_infos:
                if annotation is None:
                    raise ValueError(f"Field '{field_name}' in class '{class_name}' lacks an annotation")
                unwrapped = unwrap_type_annotation(annotation)
                if unwrapped is None:
                    raise ValueError(f"Field '{field_name}' in class '{class_name}' lacks an annotation")
                annotation_source = ast.unparse(unwrapped)
                lines.append(f"    {field_name}: TypeAlias = {annotation_source}")
        else:
            lines.append("    pass")
        lines.append("")
        lines.append("")

    output_content = "\n".join(lines)
    with target_path.open(mode="w", encoding="utf-8") as f:
        f.write(output_content)
    return target_path
