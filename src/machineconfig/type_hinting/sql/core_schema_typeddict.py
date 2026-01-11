
from typing import Any, Literal, TypedDict, TypeAlias

import datetime
import decimal
import uuid

AllTypesExampleColor: TypeAlias = Literal["red", "green", "blue"]

class OtherTableRow(TypedDict):
    id: int

class AllTypesExampleRow(TypedDict):
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

__all__: tuple[str, ...] = (
    "OtherTableRow",
    "AllTypesExampleRow",
    "AllTypesExampleColor",
)
