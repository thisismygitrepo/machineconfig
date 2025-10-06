
mkdir -p $HOME/data/binaries/machineconfig
cd $HOME/code/machineconfig
uv sync --no-dev
uv pip install nuitka
uv run python -m nuitka /home/alex/code/machineconfig/src/machineconfig/scripts/python/devops.py --onefile --standalone --output-filename=$HOME/data/binaries/machineconfig/devops
