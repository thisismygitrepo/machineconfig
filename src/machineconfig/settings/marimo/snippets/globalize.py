import marimo
from typing import Any
from types import FunctionType

app = marimo.App(width="full")

@app.cell(hide_code=True)
def _(mo: Any):
    mo.md(r"""# Globalize Lambda to Python Script""")
    return


@app.cell
def _(func: FunctionType):
    # Your snippet code
    from machineconfig.utils.meta import lambda_to_python_script
    exec(
        lambda_to_python_script(
            lambda: func(),
            in_global=True,
            import_module=False,
        ),
    )
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()