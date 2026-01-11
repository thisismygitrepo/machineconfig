
import enum
import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.sql.type_api import TypeEngine
from sqlalchemy.sql.sqltypes import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Float,
    Integer,
    Interval,
    JSON,
    LargeBinary,
    Numeric,
    SmallInteger,
    String,
    Text,
    Time,
)


@dataclass(frozen=True, slots=True)
class GeneratedModule:
    code: str
    exports: tuple[str, ...]


def _pascal_case(value: str) -> str:
    parts = [p for p in re.split(r"[^0-9A-Za-z]+", value) if p]
    if not parts:
        return "X"
    return "".join(p[:1].upper() + p[1:] for p in parts)


def _identifier(value: str) -> str:
    candidate = re.sub(r"[^0-9A-Za-z_]", "_", value)
    if not candidate:
        return "x"
    if candidate[0].isdigit():
        return f"x_{candidate}"
    return candidate


def _enum_literal_alias_name(table_name: str, column_name: str) -> str:
    return f"{_pascal_case(table_name)}{_pascal_case(column_name)}"


def _literal_union(values: Sequence[str]) -> str:
    escaped = [v.replace("\\", "\\\\").replace('"', '\\"') for v in values]
    return "Literal[" + ", ".join(f'"{v}"' for v in escaped) + "]"


@dataclass(frozen=True, slots=True)
class _TypeExpr:
    expr: str
    needs_datetime: bool
    needs_decimal: bool
    needs_uuid: bool
    needs_any: bool
    needs_literal: bool


def _union_with_none(type_expr: str, is_nullable: bool) -> str:
    return f"{type_expr} | None" if is_nullable else type_expr


def _type_expr_for_sqla_type(*, column_type: TypeEngine[Any], table_name: str, column_name: str) -> tuple[_TypeExpr, dict[str, str]]:
    enum_aliases: dict[str, str] = {}

    if isinstance(column_type, (Integer, SmallInteger, BigInteger)):
        return _TypeExpr("int", False, False, False, False, False), enum_aliases
    if isinstance(column_type, Float):
        return _TypeExpr("float", False, False, False, False, False), enum_aliases
    if isinstance(column_type, Numeric):
        return _TypeExpr("decimal.Decimal", False, True, False, False, False), enum_aliases

    if hasattr(column_type, "enum_class"):
        enum_class = getattr(column_type, "enum_class")
        if isinstance(enum_class, type) and issubclass(enum_class, enum.Enum):
            values = [str(member.value) for member in enum_class]
            alias_name = _enum_literal_alias_name(table_name=table_name, column_name=column_name)
            enum_aliases[alias_name] = _literal_union(values)
            return _TypeExpr(alias_name, False, False, False, False, True), enum_aliases

    if isinstance(column_type, (String, Text)):
        return _TypeExpr("str", False, False, False, False, False), enum_aliases
    if isinstance(column_type, Boolean):
        return _TypeExpr("bool", False, False, False, False, False), enum_aliases
    if isinstance(column_type, Date):
        return _TypeExpr("datetime.date", True, False, False, False, False), enum_aliases
    if isinstance(column_type, Time):
        return _TypeExpr("datetime.time", True, False, False, False, False), enum_aliases
    if isinstance(column_type, DateTime):
        return _TypeExpr("datetime.datetime", True, False, False, False, False), enum_aliases
    if isinstance(column_type, Interval):
        return _TypeExpr("datetime.timedelta", True, False, False, False, False), enum_aliases
    if isinstance(column_type, LargeBinary):
        return _TypeExpr("bytes", False, False, False, False, False), enum_aliases

    if isinstance(column_type, (JSON, JSONB)):
        return _TypeExpr("Any", False, False, False, True, False), enum_aliases

    if isinstance(column_type, PG_UUID):
        return _TypeExpr("uuid.UUID", False, False, True, False, False), enum_aliases

    if isinstance(column_type, PG_ARRAY):
        item_type = column_type.item_type
        item_expr, item_aliases = _type_expr_for_sqla_type(column_type=item_type, table_name=table_name, column_name=column_name)
        enum_aliases |= item_aliases
        return (
            _TypeExpr(f"list[{item_expr.expr}]", item_expr.needs_datetime, item_expr.needs_decimal, item_expr.needs_uuid, item_expr.needs_any, item_expr.needs_literal),
            enum_aliases,
        )

    return _TypeExpr("Any", False, False, False, True, False), enum_aliases


def generate_typeddict_module_code_for_tables(*, tables: Sequence[sa.Table], module_name: str) -> GeneratedModule:
    alias_defs: dict[str, str] = {}
    typed_dict_defs: list[str] = []

    needs_datetime = False
    needs_decimal = False
    needs_uuid = False
    needs_any = False
    needs_literal = False

    exports: list[str] = []

    for table in tables:
        table_name = table.name
        td_name = f"{_pascal_case(table_name)}Row"
        exports.append(td_name)

        lines: list[str] = [f"class {td_name}(TypedDict):"]
        for column in table.columns:
            col_name = column.name
            type_expr, new_aliases = _type_expr_for_sqla_type(column_type=column.type, table_name=table_name, column_name=col_name)
            alias_defs |= new_aliases

            needs_datetime = needs_datetime or type_expr.needs_datetime
            needs_decimal = needs_decimal or type_expr.needs_decimal
            needs_uuid = needs_uuid or type_expr.needs_uuid
            needs_any = needs_any or type_expr.needs_any
            needs_literal = needs_literal or type_expr.needs_literal

            field_name = _identifier(col_name)
            field_type = _union_with_none(type_expr.expr, column.nullable)
            lines.append(f"    {field_name}: {field_type}")

        typed_dict_defs.append("\n".join(lines))

    for alias_name in sorted(alias_defs.keys()):
        exports.append(alias_name)

    _ = module_name

    typing_import_names: list[str] = ["TypedDict"]
    if alias_defs:
        typing_import_names.append("TypeAlias")
    if needs_any:
        typing_import_names.insert(0, "Any")
    if needs_literal:
        typing_import_names.insert(0 if not needs_any else 1, "Literal")

    import_lines: list[str] = [
        "",
        f"from typing import {', '.join(typing_import_names)}",
    ]

    stdlib_imports: list[str] = []
    if needs_datetime:
        stdlib_imports.append("import datetime")
    if needs_decimal:
        stdlib_imports.append("import decimal")
    if needs_uuid:
        stdlib_imports.append("import uuid")
    if stdlib_imports:
        import_lines.extend(["", *stdlib_imports])

    code_parts: list[str] = []
    code_parts.extend(import_lines)

    if alias_defs:
        code_parts.append("")
        for alias_name in sorted(alias_defs.keys()):
            literal_expr = alias_defs[alias_name]
            code_parts.append(f"{alias_name}: TypeAlias = {literal_expr}")

    code_parts.append("")
    code_parts.append("\n\n".join(typed_dict_defs))

    exports_tuple = tuple(exports)
    exports_rendered = ",\n    ".join(f"\"{name}\"" for name in exports_tuple)
    code_parts.append("")
    code_parts.append("__all__: tuple[str, ...] = (\n    " + exports_rendered + ",\n)\n")

    return GeneratedModule(code="\n".join(code_parts), exports=exports_tuple)


def generate_typeddict_module_code_for_table(*, table: sa.Table, module_name: str) -> GeneratedModule:
    return generate_typeddict_module_code_for_tables(tables=(table,), module_name=module_name)


def write_generated_module(*, generated: GeneratedModule, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(generated.code, encoding="utf-8")


def write_typeddict_module_next_to_source(*, generated: GeneratedModule, source_file_path: Path) -> Path:
    output_path = source_file_path.with_name(f"{source_file_path.stem}_typeddict.py")
    write_generated_module(generated=generated, output_path=output_path)
    return output_path
