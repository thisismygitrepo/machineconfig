from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    import polars as pl


def get_polars_schema(typed_dict: type) -> "dict[str, pl.DataType]":
    import polars as pl

    def _get_polars_type(python_type: Any) -> pl.DataType:
        if python_type == str:
            return pl.String()
        if python_type == float:
            return pl.Float64()
        if python_type == int:
            return pl.Int64()
        if python_type == bool:
            return pl.Boolean()
        return pl.String()

    schema: dict[str, pl.DataType] = {}
    for k, v in typed_dict.__annotations__.items():
        schema[k] = _get_polars_type(v)
    return schema
