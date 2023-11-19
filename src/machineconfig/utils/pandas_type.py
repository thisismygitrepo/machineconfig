
# import pandas as pd
# import pandera as pa
# from pandera.typing import DataFrame, Series


# class InputSchema(pa.DataFrameModel):
#     year: Series[int] = pa.Field(gt=2000, coerce=True)
#     month: Series[int] = pa.Field(ge=1, le=12, coerce=True)
#     day: Series[int] = pa.Field(ge=0, le=365, coerce=True)

# class OutputSchema(InputSchema):
#     revenue: Series[float]

# def transform(df: DataFrame[InputSchema]) -> DataFrame[OutputSchema]:
#     df['new'] = 1
#     df['year'] = df['year'].astype(str)

#     return df


# df2 = pd.DataFrame({
#     "year": [2001, 2002, 2003],
#     "month": [3, 6, 12],
#     "day": [200, 156, 365],
# })

# # df3 = transform(df2)

# df2[InputSchema.year]

# # invalid_df = pd.DataFrame({
# #     "year": ["2001", "2002", "1999"],
# #     "month": ["3", "6", "12"],
# #     "day": ["200", "156", "365"],
# # })
# # transform(invalid_df2)
