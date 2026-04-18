# seek

`seek` is the interactive search entrypoint for file lists, text matches, file previews, AST symbols, and semantic-style symbol search.

---

## Usage

```bash
seek [OPTIONS] [PATH] [SEARCH_TERM]
```

## Arguments

| Argument | Description |
| --- | --- |
| `PATH` | Directory or file to search. Defaults to the current directory. |
| `SEARCH_TERM` | Initial query to seed the search UI. |

---

## Mode selection

The current implementation resolves modes in this order:

1. `--install-req`
2. `--symantic`
3. `--ast`
4. `--file`
5. default text search

That means `seek path query --file --ast` will still take the AST path, and `--install-req` exits before running a search.

---

## Options

| Option | Short | Description |
| --- | --- | --- |
| `--ast` | `-a` | Run AST or tree-sitter symbol search |
| `--symantic` | `-s` | Run the semantic-symbol helper workflow |
| `--extension TEXT` | `-E` | Filter file discovery by extension such as `.py` |
| `--file` | `-f` | File search mode |
| `--dotfiles` | `-d` | Toggle the dotfile-inclusive file-search path |
| `--rga` | `-A` | Swap `rg` for `rga` in text-search mode |
| `--edit` | `-e` | Open the selected result in Helix |
| `--install-req` | `-i` | Install expected helper tools and exit |

---

## Current behavior by mode

### Text search

The default mode loads a platform-specific helper script and runs an `fzf` + `rg` preview flow.

- `--rga` rewrites that script to use `ripgrep-all`
- `SEARCH_TERM` seeds the initial query
- `PATH` changes the working directory before launching the search

### File search

`--file` runs a file picker based on `fzf`.

- without `--edit`, it previews the file with `bat`
- with `--edit`, it adds a second line picker and opens the selected line in Helix
- the current implementation uses `fd --type file` for the default candidate source

### Single-file flow

If `PATH` resolves to a file, `seek` skips directory search and opens a line-oriented preview for that file instead.

When standard input is piped in and `PATH` is a directory, `seek` captures stdin into a temporary file and opens the same single-file flow against that temp file.

### AST search

`--ast` collects repository symbols, shows them with preview, and prints the selected symbol as JSON including:

- type
- name
- path
- file path
- start line
- end line
- docstring

### `--symantic`

`--symantic` runs the semantic helper workflow:

- prompts for a query if `SEARCH_TERM` is empty
- limits the search set with `--extension` when provided
- warns and exits when more than 50 files would be searched
- uses preview selection for the returned results

---

## Dependencies

`seek --install-req` currently installs these helpers:

- `fzf`
- `tv`
- `bat`
- `fd`
- `rg`
- `rga`

---

## Examples

```bash
# Default text search in the current directory
seek

# Seed the search with an initial query
seek . "TODO"

# File search with preview
seek src --file

# File search and open the chosen line in Helix
seek src --file --edit

# AST symbol search
seek src --ast

# Semantic helper search
seek src parser --symantic --extension .py

# ripgrep-all text search
seek docs invoice --rga
```

---

## Getting help

```bash
seek --help
```
