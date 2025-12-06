# Installation

Machineconfig can be installed on Windows, macOS, and Linux. We recommend using [UV](https://docs.astral.sh/uv/) for the best experience.

## Requirements

- **Python 3.13+** (automatically managed by UV)
- **UV** (recommended) or pip

---

## Install with UV (Recommended)

[UV](https://docs.astral.sh/uv/) is a fast Python package installer that handles everything for you.

### Step 1: Install UV

=== "Linux / macOS"

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

=== "Windows"

    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

### Step 2: Install Machineconfig

```bash
uv tool install --upgrade --python 3.14 machineconfig
```

This installs `machineconfig` as a global CLI tool with all its commands available immediately.

---

## Install with pip

If you prefer using pip:

```bash
pip install machineconfig
```

!!! warning "Python Version"
    Machineconfig requires Python 3.13 or higher. Make sure your Python installation meets this requirement.

---

## Verify Installation

After installation, verify that machineconfig is working:

```bash
mcfg --help
```

You should see the help output listing all available commands.

---

## Optional Dependencies

Machineconfig has optional dependencies for specific platforms and features:

### Windows-specific

```bash
pip install machineconfig[windows]
```

This includes `pywin32` for Windows-specific functionality.

### Plotting and Data Analysis

```bash
pip install machineconfig[plot]
```

This includes:

- `matplotlib`, `plotly` for visualization
- `polars`, `numpy` for data processing
- `jupyterlab`, `ipython` for interactive computing

---

## Development Installation

For contributing to machineconfig:

```bash
git clone https://github.com/thisismygitrepo/machineconfig.git
cd machineconfig
uv sync --group dev
```

This installs all development dependencies including:

- Testing: `pytest`
- Linting: `ruff`, `mypy`, `pyright`
- Documentation: `mkdocs`, `mkdocs-material`, `mkdocstrings`

---

## Upgrading

To upgrade to the latest version:

=== "UV"

    ```bash
    uv tool upgrade machineconfig
    ```

=== "pip"

    ```bash
    pip install --upgrade machineconfig
    ```

---

## Uninstalling

=== "UV"

    ```bash
    uv tool uninstall machineconfig
    ```

=== "pip"

    ```bash
    pip uninstall machineconfig
    ```
