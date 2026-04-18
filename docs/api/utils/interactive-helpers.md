# Interactive Helpers and Notifications

This slice of the utility API covers the parts of Machineconfig that talk directly to a person: small formatting helpers, interactive pickers, and email / HTML notification helpers.

The current modules are:

| Module | Purpose |
| --- | --- |
| `machineconfig.utils.accessories` | Small shared helpers such as random strings, list/timeframe splitting, rich formatting, and git-root discovery |
| `machineconfig.utils.options` | Terminal choice helpers, plus cloud and SSH selectors |
| `machineconfig.utils.options_utils.tv_options` | Preview-based selection from a mapping of names to payloads |
| `machineconfig.utils.notifications` | Markdown-to-HTML rendering plus SMTP email sending |

---

## `accessories`

Frequently used helpers from `machineconfig.utils.accessories` include:

- `randstr()` for random tokens or noun-style names
- `split_list()` for chunking lists by size or number of buckets
- `split_timeframe()` for splitting a UTC interval into fixed windows
- `pprint()`, `get_repr()`, and `human_friendly_dict()` for human-readable output
- `get_repo_root()` for locating the git repository root from a `Path`

These are intentionally small, but they show up throughout the CLI and helper layers.

---

## `choose_from_options`

`machineconfig.utils.options.choose_from_options()` is the main interactive picker.

Current behavior:

- accepts any iterable of options
- supports a numbered prompt fallback
- can use Television when `tv=True` and `tv` is installed
- supports `preview="bat"` for Television-backed previews
- accepts an optional default item
- allows custom string input when `custom_input=True`

Two implementation details matter in practice:

- the default must already be present in the option list
- multi-select is primarily implemented through the Television path; the plain prompt fallback still behaves like a single-choice prompt

Other exported helpers in the same module:

- `choose_cloud_interactively()` runs `rclone listremotes` and lets the user choose a remote
- `get_ssh_hosts()` parses `~/.ssh/config` with Paramiko
- `choose_ssh_host()` builds a Television-backed picker on top of that SSH host list

Example:

```python
from machineconfig.utils.options import choose_from_options, choose_ssh_host
from machineconfig.utils.options_utils.tv_options import choose_from_dict_with_preview

target = choose_from_options(
    options=["local", "remote", "cloud"],
    msg="Select a target",
    multi=False,
    tv=True,
    preview=None,
)

ssh_host = choose_ssh_host(multi=False)

preview_choice = choose_from_dict_with_preview(
    {
        "README.md": "# Example\n",
        "config.toml": "workers = 8\n",
    },
    extension="md",
    multi=False,
    preview_size_percent=60,
)

print(target)
print(ssh_host)
print(preview_choice)
```

---

## Preview selection

`machineconfig.utils.options_utils.tv_options.choose_from_dict_with_preview()` is the lower-level preview helper used by AST search, semantic search, and other payload-preview flows.

It takes:

- a mapping from option label to preview content
- an optional extension hint
- `multi=True` or `False`
- a preview size percentage

The implementation dispatches to Windows- or Unix-specific Television helpers.

---

## Notifications

`machineconfig.utils.notifications` currently exposes three main layers:

- `download_to_memory()` for fetching a remote asset into memory
- `md2html()` for turning Markdown into HTML through Rich's HTML exporter
- `Email` for SMTP-based email sending

Current `Email` behavior:

- `Email.get_source_of_truth()` reads config from `~/dotfiles/machineconfig/emails.ini`
- `Email.__init__()` opens either an SSL or TLS SMTP connection based on the config
- `send_message()` appends an automation footer and optionally converts Markdown to HTML
- `send_and_close()` requires a `config_name`; `config_name=None` currently raises `NotImplementedError`

Example:

```python
from machineconfig.utils.notifications import Email, md2html

html = md2html("# Report\nAll tasks finished.")
print(html[:120])

Email.send_and_close(
    config_name="primary",
    to="team@example.com",
    subject="Job finished",
    body="# Completed\nAll tasks finished successfully.",
)
```

---

## API reference

## Accessories

::: machineconfig.utils.accessories
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Options

::: machineconfig.utils.options
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Preview selection

::: machineconfig.utils.options_utils.tv_options
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Notifications

::: machineconfig.utils.notifications
    options:
      show_root_heading: true
      show_source: false
      members_order: source
