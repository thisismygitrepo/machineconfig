
from typing import TypeAlias, Literal

BACKENDS: TypeAlias = Literal["marimo", "jupyter", "vscode", "visidata", "python", "ipython"]
BACKENDS_LOOSE: TypeAlias = Literal["marimo", "m", "jupyter", "j", "vscode", "c", "visidata", "v", "python", "p", "ipython", "i"]
BACKENDS_MAP: dict[BACKENDS_LOOSE, BACKENDS] = {
    "marimo": "marimo",
    "m": "marimo",
    "jupyter": "jupyter",
    "j": "jupyter",
    "vscode": "vscode",
    "c": "vscode",
    "visidata": "visidata",
    "v": "visidata",
    "python": "python",
    "p": "python",
    "ipython": "ipython",
    "i": "ipython",
}
