
# gotch1: make sure we are in the right directory: repo root. Solution: check if .pyproject.toml exists, otherwise stop.
if [ ! -f "./pyproject.toml" ]; then
    echo "Error: pyproject.toml not found in the current directory. Please run this script from the root of a Python project."
    exit 1
fi

echo "Running linting and type checking..."

echo "Setting up environment..."
# uv add pylint pyright mypy pyrefly ruff ty --dev  # linters and type checkers
# uv add --dev cleanpy pylint pyright mypy pyrefly --upgrade-package cleanpy pylint pyright mypy pyrefly
uv add --dev pyright --upgrade-package pyright
uv add --dev pylint --upgrade-package pylint
uv add --dev mypy --upgrade-package mypy
uv add --dev pyrefly --upgrade-package pyrefly
uv add --dev cleanpy --upgrade-package cleanpy


uv add types-requests types-toml types-PyYAML types-pytz types-paramiko types-urllib3 --dev
uv add types-mysqlclient types-SQLAlchemy --dev

uv run -m cleanpy .
uv run -m ruff clean
# uv run -m ruff format .
uv run -m ruff check . --fix
uv run --no-dev --project $HOME/code/machineconfig -m machineconfig.scripts.python.ai.generate_files

mkdir .linters

echo "Running pyright..."
rm ./.linters/pyright_result.md || true
uv run pyright . > ./.linters/pyright_result.md
echo "Results of pyright are in ./.linters/pyright_result.md"

rm ./.linters/mypy_result.md || true
uv run mypy . > ./.linters/mypy_result.md
echo "Results of mypy are in ./.linters/mypy_result.md"

rm ./.linters/pylint_result.md || true
uv run pylint ./src/ > ./.linters/pylint_result.md
echo "Results of pylint are in ./.linters/pylint_result.md"

rm ./.linters/pylint_result.md || true
uv run pyrefly check . > ./.linters/pyrefly_result.md
echo "Results of pyrefly are in ./.linters/pyrefly_result.md"

rm ./.linters/ruff_result.md || true
uv run ruff check . > ./.linters/ruff_result.md
echo "Results of ruff are in ./.linters/ruff_result.md"

echo "All done! Please check the .linters directory for results."
