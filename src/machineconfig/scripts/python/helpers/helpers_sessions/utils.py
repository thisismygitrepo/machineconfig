from pathlib import Path
from typing import Literal, Optional


def balance_load(
    layout_path: str,
    max_thresh: int,
    thresh_type: Literal["number", "n", "weight", "w"],
    breaking_method: Literal["moreLayouts", "ml", "combineTabs", "ct"],
    output_path: Optional[str],
) -> None:
    """Adjust layout file to limit max tabs per layout, etc."""
    thresh_type_resolved: dict[str, Literal["number", "weight"]] = {"number": "number", "n": "number", "weight": "weight", "w": "weight"}
    breaking_method_resolved: dict[str, Literal["moreLayouts", "combineTabs"]] = {"moreLayouts": "moreLayouts", "ml": "moreLayouts", "combineTabs": "combineTabs", "ct": "combineTabs"}

    layout_path_obj = Path(layout_path).expanduser().absolute()

    from machineconfig.utils.schemas.layouts.layout_types import LayoutsFile
    import json
    layoutfile: LayoutsFile = json.loads(layout_path_obj.read_text())
    layout_configs = layoutfile["layouts"]
    from machineconfig.cluster.sessions_managers.utils.load_balancer import limit_tab_num
    new_layouts = limit_tab_num(layout_configs=layout_configs, max_thresh=max_thresh, threshold_type=thresh_type_resolved[thresh_type], breaking_method=breaking_method_resolved[breaking_method])
    layoutfile["layouts"] = new_layouts
    target_file = Path(output_path) if output_path is not None else layout_path_obj.parent / f"{layout_path_obj.stem}_adjusted_{max_thresh}_{thresh_type}_{breaking_method}.json"
    target_file.parent.mkdir(parents=True, exist_ok=True)
    target_file.write_text(data=json.dumps(layoutfile, indent=4), encoding="utf-8")
    print(f"Adjusted layout saved to {target_file}")


def create_template(name: Optional[str], num_tabs: int) -> None:
    """Create a layout template file."""
    from machineconfig.utils.schemas.layouts.layout_types import LayoutsFile, TabConfig, LayoutConfig
    tabs: list[TabConfig] = []
    for i in range(1, num_tabs + 1):
        tab: TabConfig = {
            "tabName": f"Tab{i}",
            "startDir": "~/" + str(Path.cwd().relative_to(Path.home())),
            "command": "bash",
        }
        tabs.append(tab)
    layouts: list[LayoutConfig] = [
        {
            "layoutName": f"{Path.cwd().name}Layout",
            "layoutTabs": tabs,
        }
    ]
    file: LayoutsFile = {
        "$schema": "https://bit.ly/cfglayout",  # type: ignore
        "version": "0.1",
        "layouts": layouts,
    }
    import json
    json_string = json.dumps(file, indent=4)
    if name is None:
        layout_path = Path.cwd() / "layout.json"
    else:
        layout_path = Path.cwd() / (name.replace(".json", "") + ".json")
    layout_path.parent.mkdir(parents=True, exist_ok=True)
    if layout_path.exists():
        print(f"❌ File {layout_path} already exists. Aborting to avoid overwriting.")
        return
    layout_path.write_text(json_string, encoding="utf-8")
    print(f"✅ Created layout template at {layout_path}")