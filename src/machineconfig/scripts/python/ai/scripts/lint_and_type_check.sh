
# gotch1: make sure we are in the right directory: repo root. Solution: check if .pyproject.toml exists, otherwise stop.
if [ ! -f "./pyproject.toml" ]; then
    echo "Error: pyproject.toml not found in the current directory. Please run this script from the root of a Python project."
    exit 1
fi

echo "Running linting and type checking..."

echo "Setting up environment..."
uv add pylint pyright mypy pyrefly ty --dev  # linters and type checkers
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

echo "All done! Please check the .linters directory for results."
