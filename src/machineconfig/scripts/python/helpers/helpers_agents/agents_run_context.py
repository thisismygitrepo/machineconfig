from pathlib import Path
from typing import Any, Literal, Optional
import json
import shutil
import subprocess


PROMPTS_WHERE = Literal["all", "a", "private", "p", "public", "b", "library", "l", "custom", "c"]


def _value_to_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, indent=2)


def _format_prompt_entry(value: Any) -> str:
    if not isinstance(value, dict):
        return _value_to_text(value)

    ignored_keys = {"description", "desciption", "desc", "agent"}
    filtered_items = [(str(key), item) for key, item in value.items() if str(key).lower() not in ignored_keys and item is not None]

    # Preferred human-readable layout for common prompt schema.
    prompt_text = None
    directory_text = None
    extras: list[tuple[str, Any]] = []
    for key, item in filtered_items:
        lowered = key.lower()
        if lowered == "prompt":
            prompt_text = _value_to_text(item).strip()
            continue
        if lowered == "directory":
            if isinstance(item, str) and item.strip() != "":
                directory_text = item.strip()
            continue
        extras.append((key, item))

    sections: list[str] = []
    if prompt_text is not None and prompt_text != "":
        sections.append(prompt_text)
    if directory_text is not None:
        sections.append(f"Working directory: `{directory_text}`")
    for key, item in extras:
        pretty_key = key.replace("_", " ").strip().capitalize()
        as_text = _value_to_text(item).strip()
        if "\n" in as_text:
            sections.append(f"{pretty_key}:\n{as_text}")
        else:
            sections.append(f"{pretty_key}: {as_text}")

    if len(sections) > 0:
        return "\n\n".join(sections)

    return "No prompt content configured."


def _extract_yaml_options(raw_data: Any) -> tuple[dict[str, str], dict[str, str]]:
    preview_map: dict[str, str] = {}
    context_map: dict[str, str] = {}

    if isinstance(raw_data, dict):
        for key, value in raw_data.items():
            label = str(key)
            as_text = _format_prompt_entry(value)
            preview_map[label] = as_text
            context_map[label] = as_text
    elif isinstance(raw_data, list):
        for idx, item in enumerate(raw_data):
            label = f"prompt_{idx + 1}"
            as_text = _format_prompt_entry(item)
            preview_map[label] = as_text
            context_map[label] = as_text
    else:
        as_text = _format_prompt_entry(raw_data)
        preview_map["prompt_1"] = as_text
        context_map["prompt_1"] = as_text

    return preview_map, context_map


def _resolve_context_name(raw_data: Any, context_name: str) -> str:
    cursor: Any = raw_data
    for segment in (part.strip() for part in context_name.split(".")):
        if segment == "":
            continue
        if not isinstance(cursor, dict) or segment not in cursor:
            raise ValueError(f"Context name '{context_name}' was not found in prompts YAML")
        cursor = cursor[segment]
    if cursor is None:
        raise ValueError(f"Context name '{context_name}' points to null in prompts YAML")
    return _format_prompt_entry(cursor)


def _get_default_prompts_yaml_locations(where: PROMPTS_WHERE) -> list[tuple[str, Path]]:
    from machineconfig.utils.source_of_truth import PRIVATE_SCRIPTS_ROOT, PUBLIC_SCRIPTS_ROOT, LIBRARY_SCRIPTS_ROOT
    from machineconfig.scripts.python.helpers.helpers_search.script_help import get_custom_roots

    private_prompts = PRIVATE_SCRIPTS_ROOT / "prompts" / "prompts.yaml"
    public_prompts = PUBLIC_SCRIPTS_ROOT / "prompts" / "prompts.yaml"
    library_prompts = LIBRARY_SCRIPTS_ROOT / "prompts" / "prompts.yaml"
    custom_prompts = [(f"custom_{idx}", custom_root / "prompts.yaml") for idx, custom_root in enumerate(get_custom_roots("prompts"))]

    match where:
        case "all" | "a":
            return [("private", private_prompts), ("public", public_prompts), ("library", library_prompts)] + custom_prompts
        case "private" | "p":
            return [("private", private_prompts)]
        case "public" | "b":
            return [("public", public_prompts)]
        case "library" | "l":
            return [("library", library_prompts)]
        case "custom" | "c":
            return custom_prompts


def resolve_prompts_yaml_paths(prompts_yaml_path: Optional[str], where: PROMPTS_WHERE) -> list[tuple[str, Path]]:
    if prompts_yaml_path is not None:
        return [("explicit", Path(prompts_yaml_path).expanduser().resolve())]
    return _get_default_prompts_yaml_locations(where=where)


def _prompts_yaml_template() -> str:
    return """# prompts.yaml used by `agents run`
# Top-level keys show up in interactive selection.
# Nested keys can be selected via --context-name with dot-path syntax (example: team.backend).
# Values should be prompt/context text (plain strings or multiline `|` blocks).
default: |
  You are a helpful assistant.
team:
  backend: |
    You are helping with backend engineering tasks.
  frontend: |
    You are helping with frontend engineering tasks.
"""


def ensure_prompts_yaml_exists(yaml_path: Path) -> bool:
    if yaml_path.exists():
        if not yaml_path.is_file():
            raise ValueError(f"prompts YAML path exists but is not a file: {yaml_path}")
        return False
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    yaml_path.write_text(_prompts_yaml_template(), encoding="utf-8")
    return True


def prompts_yaml_format_explanation(yaml_paths: list[tuple[str, Path]]) -> str:
    formatted_paths = "\n".join(f"- {name}: {path}" for name, path in yaml_paths) if yaml_paths else "- (none)"
    return f"""prompts YAML paths:
{formatted_paths}
Expected format:
{_prompts_yaml_template().rstrip()}
"""


def edit_prompts_yaml(yaml_path: Path) -> None:
    editor = shutil.which("hx")
    if editor is None:
        editor = shutil.which("nano")
    if editor is None:
        raise ValueError("No supported editor found. Install 'hx' or 'nano', or run without --edit")

    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run([editor, str(yaml_path)], check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Editor exited with status code {result.returncode}")


def resolve_context(context: Optional[str], context_path: Optional[str], prompts_yaml_path: Optional[str], context_name: Optional[str], where: PROMPTS_WHERE) -> str:
    if context is not None and context_path is not None:
        raise ValueError("Provide only one of --context or --context-path")
    if context_name is not None and context_path is not None:
        raise ValueError("Provide only one of --context-name or --context-path")
    if context_name is not None and context is not None:
        raise ValueError("Provide only one of --context-name or --context")

    if context is not None:
        return context

    if context_path is not None:
        context_file = Path(context_path).expanduser().resolve()
        if not context_file.exists() or not context_file.is_file():
            raise ValueError(f"--context-path must point to an existing file: {context_file}")
        return context_file.read_text(encoding="utf-8")

    from machineconfig.utils.files.read import Read
    from machineconfig.utils.options_utils.tv_options import choose_from_dict_with_preview

    yaml_locations = resolve_prompts_yaml_paths(prompts_yaml_path=prompts_yaml_path, where=where)
    if prompts_yaml_path is not None and len(yaml_locations) == 1:
        ensure_prompts_yaml_exists(yaml_path=yaml_locations[0][1])

    existing_yaml_locations = [(location_name, yaml_path) for location_name, yaml_path in yaml_locations if yaml_path.exists() and yaml_path.is_file()]
    if len(existing_yaml_locations) == 0:
        if prompts_yaml_path is not None:
            raise ValueError(f"No prompts YAML entries found in explicit file: {yaml_locations[0][1]}")
        searched = ", ".join(str(yaml_path) for _, yaml_path in yaml_locations)
        raise ValueError(f"No prompts YAML files found for --where '{where}'. Searched: {searched}")

    if context_name is not None:
        for _, yaml_path in existing_yaml_locations:
            yaml_data = Read.yaml(yaml_path)
            try:
                return _resolve_context_name(raw_data=yaml_data, context_name=context_name)
            except ValueError:
                pass
        searched = ", ".join(str(yaml_path) for _, yaml_path in existing_yaml_locations)
        raise ValueError(f"Context name '{context_name}' was not found in prompts YAML files: {searched}")

    preview_map: dict[str, str] = {}
    context_map: dict[str, str] = {}
    for location_name, yaml_path in existing_yaml_locations:
        yaml_data = Read.yaml(yaml_path)
        file_preview_map, file_context_map = _extract_yaml_options(yaml_data)
        for key, preview in file_preview_map.items():
            label = f"{location_name}.{key}" if where in ("all", "a") else key
            if label in preview_map:
                label = f"{label}@{yaml_path.name}"
            preview_map[label] = preview
            context_map[label] = file_context_map[key]
    if len(preview_map) == 0:
        searched = ", ".join(str(yaml_path) for _, yaml_path in existing_yaml_locations)
        raise ValueError(f"No prompt entries found in prompts YAML files: {searched}")

    chosen_key = choose_from_dict_with_preview(options_to_preview_mapping=preview_map, extension="yaml", multi=False, preview_size_percent=45.0)
    if chosen_key is None:
        raise SystemExit(1)
    return context_map[chosen_key]
