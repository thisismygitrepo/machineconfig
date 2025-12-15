import ast
from pathlib import Path

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


def generate_names_file(source_file_path: Path, output_file_path: Path, search_paths: list[Path] | None = None) -> Path:
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

    lines: list[str] = ["from collections.abc import Iterable", "from typing import Annotated, Any, Literal, TypeAlias, TYPE_CHECKING, overload", ""]

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

    lines.append("")
    lines.append("if TYPE_CHECKING:")
    lines.append("    import polars as pl")
    all_type_checking_imports = sorted(set(needed_local_classes) - set(target_class_names))
    if all_type_checking_imports:
        lines.append(f"    from {source_module} import {', '.join(all_type_checking_imports)}")
    lines.append("")
    lines.append("")

    for class_name, field_infos in target_classes:
        source_module = _get_module_name_from_path(source_file_path)
        stripped_field_infos = [(fn, ann) for fn, ann, _ in field_infos]
        lines.extend(generate_for_class(class_name, stripped_field_infos, source_module))

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
