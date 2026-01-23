import enum
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, Interval, JSON, LargeBinary, MetaData, Numeric, SmallInteger, String, Table, Text, Time
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

from typing import Literal, TypeAlias

class ColorEnum(enum.Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


T1: TypeAlias = Literal["t1", "t3"]
T1_ENUM: sa.Enum = sa.Enum("t1", "t3", name="t1_enum")

metadata: MetaData = MetaData()

other_table: Table = Table(
    "other_table",
    metadata,
    Column("id", Integer, primary_key=True, comment="Referenced by all_types_example.related_id"),
)

all_types_example: Table = Table(
    "all_types_example",
    metadata,
    Column("small_num", SmallInteger, comment="SMALLINT (~int16, Postgres int2)"),
    Column("id", Integer, primary_key=True, comment="INTEGER (~int32, Postgres int4)"),
    Column("big_num", BigInteger, comment="BIGINT (~int64, Postgres int8)"),
    Column("int128_num", Numeric(precision=38, scale=0), comment="NUMERIC(38,0) for ~int128 range (DBs lack a standard int128 type)"),

    Column("float_num", Float, comment="FLOAT (precision-dependent; SQL has no standard float16 type)"),
    Column("float32_num", Float(precision=24), comment="FLOAT(24) ~float32 (Postgres float4)"),  # AKA REAL
    Column("float64_num", Float(precision=53), comment="FLOAT(53) ~float64 (Postgres float8)"),  # AKA DOUBLE PRECISION
    Column(
        "decimal_value",
        Numeric(precision=12, scale=4),
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
    Column("t1_value", T1_ENUM, nullable=False, comment="Enum literal values: t1 | t3"),
    Column("uuid_field", UUID(as_uuid=True), default=uuid4, comment="GUID/UUID (128-bit unique identifier)"),
    Column("int_array", ARRAY(Integer), comment="ARRAY of INTEGER (~list[int32])"),
    Column("str_array", ARRAY(String), comment="ARRAY of VARCHAR strings"),
    Column("unique_code", String(20), unique=True, nullable=False, comment="Unique code"),
    Column("created_at", DateTime, server_default=sa.func.now(), comment="timestamp default now"),
    Column("related_id", Integer, ForeignKey("other_table.id"), comment="Foreign key reference"),
)


if __name__ == "__main__":
    q = all_types_example
    # q.colo