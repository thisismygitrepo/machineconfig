
from typing import Any, Literal, TypedDict, TypeAlias
import polars as pl

import datetime
import decimal
import uuid

AllTypesExampleColor: TypeAlias = Literal["red", "green", "blue"]

class OtherTableRow(TypedDict):
    id: int

class AllTypesExample_Row(TypedDict):
    id: int
    small_num: int | None
    big_num: int | None
    float_num: float | None
    decimal_value: decimal.Decimal | None
    short_str: str | None
    long_text: str | None
    is_active: bool | None
    date_field: datetime.date | None
    time_field: datetime.time | None
    datetime_field: datetime.datetime | None
    interval_field: datetime.timedelta | None
    binary_data: bytes | None
    json_data: Any | None
    jsonb_data: Any | None
    color: AllTypesExampleColor
    uuid_field: uuid.UUID | None
    int_array: list[int] | None
    str_array: list[str] | None
    unique_code: str
    created_at: datetime.datetime | None
    related_id: int | None

class AllTypesExample_Types:
    id: TypeAlias = int
    small_num: TypeAlias = int | None
    big_num: TypeAlias = int | None
    float_num: TypeAlias = float | None
    decimal_value: TypeAlias = decimal.Decimal | None
    short_str: TypeAlias = str | None
    long_text: TypeAlias = str | None
    is_active: TypeAlias = bool | None
    date_field: TypeAlias = datetime.date | None
    time_field: TypeAlias = datetime.time | None
    datetime_field: TypeAlias = datetime.datetime | None
    interval_field: TypeAlias = datetime.timedelta | None
    binary_data: TypeAlias = bytes | None
    json_data: TypeAlias = Any | None
    jsonb_data: TypeAlias = Any | None
    color: TypeAlias = AllTypesExampleColor
    uuid_field: TypeAlias = uuid.UUID | None
    int_array: TypeAlias = list[int] | None
    str_array: TypeAlias = list[str] | None
    unique_code: TypeAlias = str
    created_at: TypeAlias = datetime.datetime | None
    related_id: TypeAlias = int | None
AllTypeExample_ColumnsType: TypeAlias = Literal[
    "id",
    "small_num",
    "big_num",
    "float_num",
    "decimal_value",
    "short_str",
    "long_text",
    "is_active",
    "date_field",
    "time_field",
    "datetime_field",
    "interval_field",
    "binary_data",
    "json_data",
    "jsonb_data",
    "color",
    "uuid_field",
    "int_array",
    "str_array",
    "unique_code",
    "created_at",
    "related_id",
]

class AllTypeExample_Columns:
    id: Literal["id"] = "id"
    small_num: Literal["small_num"] = "small_num"
    big_num: Literal["big_num"] = "big_num"
    float_num: Literal["float_num"] = "float_num"
    decimal_value: Literal["decimal_value"] = "decimal_value"
    short_str: Literal["short_str"] = "short_str"
    long_text: Literal["long_text"] = "long_text"
    is_active: Literal["is_active"] = "is_active"
    date_field: Literal["date_field"] = "date_field"
    time_field: Literal["time_field"] = "time_field"
    datetime_field: Literal["datetime_field"] = "datetime_field"
    interval_field: Literal["interval_field"] = "interval_field"
    binary_data: Literal["binary_data"] = "binary_data"
    json_data: Literal["json_data"] = "json_data"
    jsonb_data: Literal["jsonb_data"] = "jsonb_data"
    color: Literal["color"] = "color"
    uuid_field: Literal["uuid_field"] = "uuid_field"
    int_array: Literal["int_array"] = "int_array"
    str_array: Literal["str_array"] = "str_array"
    unique_code: Literal["unique_code"] = "unique_code"
    created_at: Literal["created_at"] = "created_at"
    related_id: Literal["related_id"] = "related_id"


class AllTypesExample_wrapper:
    ct: AllTypeExample_ColumnsType
    c: AllTypeExample_Columns
    r: AllTypesExample_Row
    t: AllTypesExample_Types
    @staticmethod
    def get_polars_schema(): pass
    def __init__(self, df: "pl.DataFrame") -> None:
        self.df = df
