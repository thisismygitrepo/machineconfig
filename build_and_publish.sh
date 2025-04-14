#!/bin/bash

# Build and publish
uv build

# Extract PyPI token from .pypirc file
PYPI_TOKEN=$(grep -A2 "\[pypi\]" ~/dotfiles/creds/msc/.pypirc | grep "password" | sed 's/password = //')
uv publish --token $PYPI_TOKEN

