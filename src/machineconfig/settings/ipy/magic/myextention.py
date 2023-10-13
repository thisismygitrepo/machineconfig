
"""G
"""

# from crocodile.core import Display
from IPython.core.magic import register_line_magic
import pandas as pd
 

@register_line_magic("human")  # type: ignore
def make_dataframe_human_readable(df: 'pd.DataFrame'):
    df2 = df.copy()
    return df2
