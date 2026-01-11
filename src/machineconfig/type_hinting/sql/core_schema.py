import enum
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, Interval, JSON, LargeBinary, MetaData, Numeric, SmallInteger, String, Table, Text, Time
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID


class ColorEnum(enum.Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


metadata: MetaData = MetaData()

other_table: Table = Table(
    "other_table",
    metadata,
    Column("id", Integer, primary_key=True, comment="Referenced by all_types_example.related_id"),
)

all_types_example: Table = Table(
    "all_types_example",
    metadata,
    Column("id", Integer, primary_key=True, comment="Typical SQL INTEGER (~int32 on many databases)"),
    Column("small_num", SmallInteger, comment="SMALLINT (~int16)"),
    Column("big_num", BigInteger, comment="BIGINT (~int64)"),
    Column("float_num", Float, comment="FLOAT → typically float32/float64 depending on precision"),
    Column(
        "decimal_value",
        Numeric(12, 4),
        comment="NUMERIC/DECIMAL fixed precision; client uses python Decimal by default (~exact decimal, not float)",
    ),
    Column("short_str", String(50), comment="VARCHAR(n) fixed limit"),
    Column("long_text", Text, comment="TEXT (unbounded string)"),
    Column("is_active", Boolean, comment="BOOLEAN (True/False)"),
    Column("date_field", Date, comment="DATE only (year/month/day)"),
    Column("time_field", Time, comment="TIME only (hh:mm:ss)"),
    Column("datetime_field", DateTime, comment="TIMESTAMP without timezone"),
    Column("interval_field", Interval, comment="INTERVAL type (duration)"),
    Column("binary_data", LargeBinary, comment="Large binary / BLOB"),
    Column("json_data", JSON, comment="Generic JSON type (engine specific)"),
    Column("jsonb_data", JSONB, comment="PostgreSQL JSONB (binary JSON)"),
    Column("color", sa.Enum(ColorEnum), nullable=False, comment="ENUM type"),
    Column("uuid_field", UUID(as_uuid=True), default=uuid4, comment="GUID/UUID (128-bit unique identifier)"),
    Column("int_array", ARRAY(Integer), comment="ARRAY of INTEGER (~list[int32])"),
    Column("str_array", ARRAY(String), comment="ARRAY of VARCHAR strings"),
    Column("unique_code", String(20), unique=True, nullable=False, comment="Unique code"),
    Column("created_at", DateTime, server_default=sa.func.now(), comment="timestamp default now"),
    Column("related_id", Integer, ForeignKey("other_table.id"), comment="Foreign key reference"),
)


__all__: tuple[str, ...] = (
    "ColorEnum",
    "all_types_example",
    "metadata",
    "other_table",
)

if __name__ == "__main__":
    q = all_types_example
    # q.colo