
sudo nala install ccache patchelf -y

mkdir -p $HOME/data/binaries/machineconfig
cd $HOME/code/machineconfig
rm -rfd build
rm -rfd .venv
uv sync --no-dev
uv pip install nuitka
uv run --no-dev python -m nuitka /home/alex/code/machineconfig/src/machineconfig/scripts/python/devops.py --onefile --standalone --output-filename=devops  --output-dir=./build
