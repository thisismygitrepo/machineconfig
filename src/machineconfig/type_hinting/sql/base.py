# from uuid import uuid4
# import enum
# from datetime import date, datetime, time, timedelta

# import sqlalchemy as sa
# from sqlalchemy import (
#     BigInteger,
#     Boolean,
#     CHAR,
#     Date,
#     DateTime,
#     Float,
#     Integer,
#     Interval,
#     LargeBinary,
#     Numeric,
#     SmallInteger,
#     String,
#     Text,
#     Time,
#     JSON,
#     Enum,
# )
# from sqlalchemy.dialects.postgresql import (
#     ARRAY,
#     JSONB,
#     UUID,
# )
# from sqlalchemy.orm import (
#     DeclarativeBase,
#     Mapped,
#     mapped_column,
# )

# # Python enum type — stored generally as a VARCHAR or ENUM in the DB
# class ColorEnum(enum.Enum):
#     RED = "red"
#     GREEN = "green"
#     BLUE = "blue"

# class Base(DeclarativeBase):
#     pass

# class AllTypesExample(Base):
#     __tablename__ = "all_types_example"

#     # ----------------------------------
#     # Integer types
#     # ----------------------------------

#     id: Mapped[int] = mapped_column(
#         Integer,
#         primary_key=True,
#         comment="Typical SQL INTEGER (~int32 on many databases)"
#     )

#     small_num: Mapped[int] = mapped_column(
#         SmallInteger,
#         comment="SMALLINT (~int16)"
#     )

#     big_num: Mapped[int] = mapped_column(
#         BigInteger,
#         comment="BIGINT (~int64)"
#     )

#     # ----------------------------------
#     # Floating-point & precision numbers
#     # ----------------------------------

#     float_num: Mapped[float] = mapped_column(
#         Float,
#         comment="FLOAT → typically float32/float64 depending on precision [Float maps to SQL FLOAT/REAL] (SQLAlchemy docs) :contentReference[oaicite:0]{index=0}"
#     )

#     decimal_value: Mapped[float] = mapped_column(
#         Numeric(12, 4),
#         comment="NUMERIC/DECIMAL fixed precision; client uses python Decimal by default (~exact decimal, not float)"
#     )

#     # ----------------------------------
#     # Strings, text, character
#     # ----------------------------------

#     short_str: Mapped[str] = mapped_column(
#         String(50),
#         comment="VARCHAR(n) fixed limit"
#     )

#     long_text: Mapped[str] = mapped_column(
#         Text,
#         comment="TEXT (unbounded string)"
#     )

#     # ----------------------------------
#     # Boolean
#     # ----------------------------------

#     is_active: Mapped[bool] = mapped_column(
#         Boolean,
#         comment="BOOLEAN (True/False)"
#     )

#     # ----------------------------------
#     # Dates and times
#     # ----------------------------------

#     date_field: Mapped[date] = mapped_column(
#         Date,
#         comment="DATE only (year/month/day)"
#     )

#     time_field: Mapped[time] = mapped_column(
#         Time,
#         comment="TIME only (hh:mm:ss)"
#     )

#     datetime_field: Mapped[datetime] = mapped_column(
#         DateTime,
#         comment="TIMESTAMP without timezone"
#     )

#     interval_field: Mapped[timedelta] = mapped_column(
#         Interval,
#         comment="INTERVAL type (duration)"
#     )

#     # ----------------------------------
#     # Binary / blobs
#     # ----------------------------------

#     binary_data: Mapped[bytes] = mapped_column(
#         LargeBinary,
#         comment="Large binary / BLOB"
#     )

#     # ----------------------------------
#     # JSON
#     # ----------------------------------

#     json_data: Mapped[dict] = mapped_column(
#         JSON,
#         comment="Generic JSON type (engine specific)"
#     )

#     jsonb_data: Mapped[dict] = mapped_column(
#         JSONB,
#         comment="PostgreSQL JSONB (binary JSON)"
#     )

#     # ----------------------------------
#     # Enum
#     # ----------------------------------

#     color: Mapped[ColorEnum] = mapped_column(
#         Enum(ColorEnum),
#         nullable=False,
#         comment="ENUM type"
#     )

#     # ----------------------------------
#     # UUID
#     # ----------------------------------

#     uuid_field: Mapped[str] = mapped_column(
#         UUID(as_uuid=True),
#         default=uuid4,
#         comment="GUID/UUID (128-bit unique identifier)"
#     )

#     # ----------------------------------
#     # Array — PostgreSQL only
#     # ----------------------------------

#     int_array: Mapped[list[int]] = mapped_column(
#         ARRAY(Integer),
#         comment="ARRAY of INTEGER (~list[int32])"
#     )

#     str_array: Mapped[list[str]] = mapped_column(
#         ARRAY(String),
#         comment="ARRAY of VARCHAR strings"
#     )

#     # ----------------------------------
#     # Constraints & defaults
#     # ----------------------------------

#     unique_code: Mapped[str] = mapped_column(
#         String(20),
#         unique=True,
#         nullable=False,
#         comment="Unique code"
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime,
#         server_default=sa.func.now(),
#         comment="timestamp default now"
#     )

#     # ----------------------------------
#     # Foreign key
#     # ----------------------------------

#     related_id: Mapped[int] = mapped_column(
#         Integer,
#         sa.ForeignKey("other_table.id"),
#         comment="Foreign key reference"
#     )


# if __name__ == "__main__":
#     # Example usage: create the tables in an in-memory SQLite database
#     q = AllTypesExample()
#     q.created_at.__qualname__
