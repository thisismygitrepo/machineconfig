import polars as pl
from polars._typing import PolarsDataType
from sqlalchemy import Table
from sqlalchemy.sql.sqltypes import BigInteger, Boolean, Date, DateTime, Enum as SAEnum, Float, Integer, Interval, JSON, LargeBinary, Numeric, SmallInteger, String, Text, Time
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from typing import Optional


def sqlalchemy_type_to_polars(sa_type: object, map_decimal_to_closest_arithmetic_type: bool) -> PolarsDataType:
    # Order matters due to SQLAlchemy inheritance:
    # - SmallInteger/BigInteger inherit from Integer, so check them first
    # - Float inherits from Numeric, so check Float before Numeric
    # - Enum inherits from String, so check Enum before String
    if isinstance(sa_type, SmallInteger):
        return pl.Int16
    if isinstance(sa_type, BigInteger):
        return pl.Int64
    if isinstance(sa_type, Integer):
        return pl.Int32
    if isinstance(sa_type, Float):
        # SQLAlchemy Float precision is specified in bits (mantissa bits) or decimal digits depending on backend.
        # IEEE 754: Float32 has 24-bit mantissa (~7 decimal digits), Float64 has 53-bit mantissa (~15-16 decimal digits).
        # We interpret precision as:
        #   - If p <= 24: assume bits, maps to Float32
        #   - If 24 < p <= 53: assume bits, maps to Float64
        #   - If p is None: default to Float64 for safety
        # For decimal-digit interpretation (common in SQL REAL/FLOAT(p)):
        #   - p <= 7 decimal digits: Float32 is sufficient
        #   - p <= 15 decimal digits: Float64 is sufficient
        # We use bit-based thresholds as primary (SQLAlchemy default), with fallback heuristics.
        p: Optional[int] = getattr(sa_type, "precision", None)
        if p is None:
            return pl.Float64  # default to Float64 for maximum safety when precision unspecified
        if p <= 7:  # p interpreted as decimal digits, Float32 has ~7 decimal digits precision
            return pl.Float32
        if p <= 24:  # p interpreted as mantissa bits, Float32 has 24-bit mantissa
            return pl.Float32
        if p <= 53:  # p interpreted as mantissa bits, Float64 has 53-bit mantissa
            return pl.Float64
        return pl.Float64  # p > 53, Float64 is the best we have in Polars
    if isinstance(sa_type, Numeric):
        p: Optional[int] = getattr(sa_type, "precision", None)
        s: int = getattr(sa_type, "scale", None) or 0
        if map_decimal_to_closest_arithmetic_type:
            if s == 0:
                # scale=0 means integer-like; pick smallest int type that fits
                # precision = max decimal digits: Int16 ~4, Int32 ~9, Int64 ~18, Int128 ~38
                if p is None or p > 38:
                    return pl.Decimal(precision=p, scale=0)
                if p <= 4:  # means range of -(10^4)-1 to (10^4)-1, which easily fits in Int16 that has range -2^15 to 2^15-1
                    return pl.Int16  # prefer this because it has smaller memory footprint and is faster, and fixed in size (2 bytes)
                if p <= 9:  # means range of -(10^9)-1 to (10^9)-1, which easily fits in Int32 that has range -2^31 to 2^31-1
                    return pl.Int32  # prefer this because it has smaller memory footprint and is faster, and fixed in size (4 bytes)
                if p <= 18:  # means range of -(10^18)-1 to (10^18)-1, which easily fits in Int64 that has range -2^63 to 2^63-1
                    return pl.Int64  # prefer this because it has smaller memory footprint and is faster, and fixed in size (8 bytes)
                return pl.Decimal(precision=p, scale=0)  # p <= 38, use Decimal as Int128 proxy
            else:
                # scale > 0 means fractional; map to float based on precision and scale
                # IEEE 754 significant decimal digits:
                #   - Float16: ~3-4 decimal digits precision (11-bit significand)
                #   - Float32: ~7 decimal digits precision (24-bit significand)
                #   - Float64: ~15-16 decimal digits precision (53-bit significand)
                # We need a float that can represent BOTH:
                #   - p total significant digits (integer + fractional parts)
                #   - s fractional digits (scale)
                # The float must satisfy: precision >= p AND precision >= s
                # So we take the maximum of both requirements.
                # If required precision exceeds Float64 capability, fall back to Decimal.
                if p is None:
                    return pl.Float64  # default to Float64 for safety when precision unspecified
                required_precision = max(p, s)
                if required_precision <= 3:
                    return pl.Float16  # ~3-4 decimal digits, suitable for very low precision decimals
                if required_precision <= 7:
                    return pl.Float32  # ~7 decimal digits, suitable for moderate precision decimals
                if required_precision <= 15:
                    return pl.Float64  # ~15-16 decimal digits, for high precision decimals
                return pl.Decimal(precision=p, scale=s)  # precision exceeds Float64, preserve with Decimal
        return pl.Decimal(precision=p, scale=s)
    if isinstance(sa_type, SAEnum):
        return pl.Categorical
    if isinstance(sa_type, (String, Text)):
        return pl.String
    if isinstance(sa_type, Boolean):
        return pl.Boolean
    if isinstance(sa_type, Date):
        return pl.Date
    if isinstance(sa_type, Time):
        return pl.Time
    if isinstance(sa_type, DateTime):
        return pl.Datetime
    if isinstance(sa_type, Interval):
        return pl.Duration
    if isinstance(sa_type, LargeBinary):
        return pl.Binary
    if isinstance(sa_type, (JSON, JSONB)):
        return pl.String
    if isinstance(sa_type, UUID):
        return pl.String
    if isinstance(sa_type, ARRAY):
        item_type = getattr(sa_type, "item_type", None)
        if item_type is not None:
            inner = sqlalchemy_type_to_polars(item_type, map_decimal_to_closest_arithmetic_type)
            return pl.List(inner)
        return pl.List(pl.String)
    return pl.String


def sqlalchemy_table_to_polars_schema(table: Table) -> dict[str, PolarsDataType]:
    schema: dict[str, PolarsDataType] = {}
    for column in table.columns:
        col_name: str = column.name
        pl_type = sqlalchemy_type_to_polars(column.type, map_decimal_to_closest_arithmetic_type=True)
        schema[col_name] = pl_type
    return schema


if __name__ == "__main__":
    from machineconfig.type_hinting.sql.examples.proto_type_guidance.core_schema import all_types_example, other_table

    schema = sqlalchemy_table_to_polars_schema(all_types_example)
    for name, dtype in schema.items():
        print(f"{name}: {dtype}")

    print("\n--- other_table ---")
    schema2 = sqlalchemy_table_to_polars_schema(other_table)
    for name, dtype in schema2.items():
        print(f"{name}: {dtype}")
