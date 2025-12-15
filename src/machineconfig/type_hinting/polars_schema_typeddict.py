from __future__ import annotations

from typing import Any, ReadOnly, TYPE_CHECKING, get_args, get_origin

if TYPE_CHECKING:
    import polars as pl


def unwrap_type(python_type: Any) -> Any:
    """Unwrap ReadOnly and other type wrappers to get the inner type."""
    origin = get_origin(python_type)
    if origin is ReadOnly:
        args = get_args(python_type)
        return args[0] if args else python_type
    return python_type


def get_polars_type(python_type: Any) -> pl.DataType:
    """Convert Python types to appropriate Polars types, handling ReadOnly wrappers."""
    import polars as pl

    unwrapped = unwrap_type(python_type)
    if unwrapped is str:
        return pl.String()
    if unwrapped is float:
        return pl.Float64()
    if unwrapped is int:
        return pl.Int64()
    if unwrapped is bool:
        return pl.Boolean()
    return pl.String()


def get_polars_schema_from_typeddict(typed_dict: type) -> dict[str, pl.DataType]:
    """Convert a TypedDict to a Polars schema, properly handling ReadOnly wrappers."""
    schema: dict[str, pl.DataType] = {}
    for k, v in typed_dict.__annotations__.items():
        schema[k] = get_polars_type(v)
    return schema


def get_polars_df_random_data_from_typeddict(typed_dict: type, n_rows: int) -> pl.DataFrame:
    """Generate a Polars DataFrame with random data based on a TypedDict definition."""
    import polars as pl
    import random
    import secrets

    data: dict[str, pl.Series] = {}
    for k, v in typed_dict.__annotations__.items():
        unwrapped = unwrap_type(v)
        if unwrapped is str:
            data[k] = pl.Series([secrets.token_hex(8) for _ in range(n_rows)])
        elif unwrapped is int:
            data[k] = pl.Series(random.choices(range(-1000, 1000), k=n_rows))
        elif unwrapped is float:
            data[k] = pl.Series([random.uniform(-1000.0, 1000.0) for _ in range(n_rows)])
        elif unwrapped is bool:
            data[k] = pl.Series(random.choices([True, False], k=n_rows))
        elif unwrapped is bytes:
            data[k] = pl.Series([secrets.token_bytes(16) for _ in range(n_rows)])
        elif get_origin(unwrapped) is list:
            data[k] = pl.Series([[random.randint(0, 100) for _ in range(3)] for _ in range(n_rows)])
        else:
            data[k] = pl.Series([None] * n_rows)

    return pl.DataFrame(data, schema=get_polars_schema_from_typeddict(typed_dict))
