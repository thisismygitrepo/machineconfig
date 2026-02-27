#!/usr/bin/env bash

uv cache clean --force
rm -rfd .venv
uv add --no-cache cryptography fire gitpython joblib paramiko psutil pyyaml questionary randomname rclone-python requests rich tenacity typer
uv add --no-cache --optional windows pywin32
uv add --no-cache --optional plot sqlalchemy ipykernel ipython jupyterlab kaleido matplotlib nbformat numpy plotly polars python-magic
uv add --no-cache --group dev aider build cleanpy cowsay duckdb gdown github-copilot-sdk ipdb ipykernel ipython kaleido marimo matplotlib mkdocs mkdocs-autorefs mkdocs-material mkdocstrings mkdocstrings-python mypy numpy pandas plotly polars pre-commit pudb pydantic pydeps pyinstaller pylint pylsp-mypy pymupdf pypdf pyrefly pyright pytest python-lsp-server qrcode ruff ruff-lsp sqlalchemy textual trogon ty types-mysqlclient types-paramiko types-pytz types-pyyaml types-requests types-sqlalchemy types-toml types-urllib3 vt-py yapf
uv add --no-cache --group other duckdb-engine pycrucible vt-py
uv add --no-cache --group plot duckdb ipykernel ipython jupyterlab kaleido matplotlib nbformat numpy plotly polars python-magic sqlalchemy
