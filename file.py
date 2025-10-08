import marimo

__generated_with = "0.16.5"
app = marimo.App(
    width="full",
    auto_download=["html", "ipynb"],
    sql_output="polars",
)


@app.cell
def _():
    import machineconfig
    print(machineconfig.__file__)
    return


@app.cell
def _():
    import plotly.express as px
    import numpy as np

    px.line(np.arange(10))
    return


@app.cell
def _():
    print(1+3
         )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
