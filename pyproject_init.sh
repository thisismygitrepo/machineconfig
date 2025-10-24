#!/bin/bash
set -e

uv cache clean --force

uv add --no-cache cryptography fire joblib paramiko randomname requests rich tenacity psutil gitpython pyfzf rclone-python questionary typer-slim typer
uv add --no-cache --group windows pywin32
uv add --no-cache --group plot sqlalchemy ipykernel ipython jupyterlab kaleido matplotlib nbformat numpy plotly polars python-magic
uv add --no-cache --dev aider build cleanpy cowsay ipdb ipykernel ipython matplotlib mypy numpy pandas plotly polars pre-commit pudb pylint pymupdf pypdf pyrefly pyright pytest ruff sqlalchemy textual trogon ty types-mysqlclient types-paramiko types-pytz types-pyyaml types-requests types-sqlalchemy types-toml types-urllib3
uv add --no-cache --group other duckdb-engine pycrucible vt-py
