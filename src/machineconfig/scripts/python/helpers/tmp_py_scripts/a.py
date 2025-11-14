
"""
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "rich",
#   "polars",
#   "typer>=0.12",
#   "loguru",
#   "numpy",
# ]
# ///

"""


def main():
    """a,b,c"""
    print("This is a helper function in a.py")
    import numpy as np
    print("Numpy version:", np.__version__)


if __name__ == "__main__":
    main()
