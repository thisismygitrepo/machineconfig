#!/usr/bin/env python3
import json
import logging
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from machineconfig.cluster.sessions_managers.zellij_utils.monitoring_types import ActiveSessionInfo, StartResult
from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig

if TYPE_CHECKING:
    from machineconfig.cluster.sessions_managers.zellij_local import ZellijLayoutGenerator


logger = logging.getLogger(__name__)
TMP_SERIALIZATION_DIR = Path.home() / "tmp_results" / "zellij_sessions" / "serialized"


def list_saved_sessions() -> list[str]:
    """List all saved session IDs."""
    if not TMP_SERIALIZATION_DIR.exists():
        return []
    sessions = []
    for item in TMP_SERIALIZATION_DIR.iterdir():
        if item.is_dir() and (item / "metadata.json").exists():
            sessions.append(item.name)
    return sorted(sessions)


def delete_session(session_id: str) -> bool:
    """Delete a saved session."""
    session_dir = TMP_SERIALIZATION_DIR / session_id
    if not session_dir.exists():
        logger.warning(f"Session directory not found: {session_dir}")
        return False
    try:
        shutil.rmtree(session_dir)
        logger.info(f"✅ Deleted session: {session_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete session {session_id}: {e}")
        return False


def get_all_session_names(managers: list["ZellijLayoutGenerator"]) -> list[str]:
    """Get all managed session names."""
    return [manager.session_name for manager in managers]


def attach_to_session(managers: list["ZellijLayoutGenerator"], session_name: Optional[str]) -> str:
    """
    Generate command to attach to a specific session or list attachment commands for all.

    Args:
        managers: List of ZellijLayoutGenerator instances
        session_name: Specific session to attach to, or None for all sessions

    Returns:
        Command string to attach to session(s)
    """
    if session_name:
        for manager in managers:
            if manager.session_name == session_name:
                return f"zellij attach {session_name}"
        raise ValueError(f"Session '{session_name}' not found")
    else:
        commands: list[str] = []
        for manager in managers:
            commands.append(f"# Attach to session '{manager.session_name}':")
            commands.append(f"zellij attach {manager.session_name}")
            commands.append("")
        return "\n".join(commands)


def list_active_sessions(managers: list["ZellijLayoutGenerator"]) -> list[ActiveSessionInfo]:
    """List currently active zellij sessions managed by this instance."""
    active_sessions: list[ActiveSessionInfo] = []
    try:
        result = subprocess.run(["zellij", "list-sessions"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            all_sessions = result.stdout.strip().split("\n") if result.stdout.strip() else []
            for manager in managers:
                session_name = manager.session_name
                is_active = any(session_name in session for session in all_sessions)
                tab_info = []
                tab_count = 0
                if manager.layout_config:
                    tab_count = len(manager.layout_config["layoutTabs"])
                    tab_info = [tab["tabName"] for tab in manager.layout_config["layoutTabs"]]
                active_sessions.append({"session_name": session_name, "is_active": is_active, "tab_count": tab_count, "tabs": tab_info})
    except Exception as e:
        logger.error(f"Error listing active sessions: {e}")
    return active_sessions


def save_manager(session_layouts: list[LayoutConfig], managers: list["ZellijLayoutGenerator"], session_name_prefix: str, session_id: Optional[str]) -> str:
    """Save the manager state to disk."""
    if session_id is None:
        import uuid
        session_id = str(uuid.uuid4())[:8]
    session_dir = TMP_SERIALIZATION_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    config_file = session_dir / "session_layouts.json"
    text = json.dumps(session_layouts, indent=2, ensure_ascii=False)
    config_file.write_text(text, encoding="utf-8")
    metadata = {"session_name_prefix": session_name_prefix, "created_at": str(datetime.now()), "num_managers": len(managers), "sessions": [item["layoutName"] for item in session_layouts], "manager_type": "ZellijLocalManager"}
    metadata_file = session_dir / "metadata.json"
    text = json.dumps(metadata, indent=2, ensure_ascii=False)
    metadata_file.write_text(text, encoding="utf-8")
    managers_dir = session_dir / "managers"
    managers_dir.mkdir(exist_ok=True)
    for i, manager in enumerate(managers):
        manager_data = {"session_name": manager.session_name, "layout_config": manager.layout_config, "layout_path": manager.layout_path}
        manager_file = managers_dir / f"manager_{i}_{manager.session_name}.json"
        text = json.dumps(manager_data, indent=2, ensure_ascii=False)
        manager_file.write_text(text, encoding="utf-8")
    logger.info(f"✅ Saved ZellijLocalManager session to: {session_dir}")
    return session_id


def load_manager(session_id: str):
    """Load a saved manager state from disk and return the data needed to reconstruct ZellijLocalManager."""
    from machineconfig.cluster.sessions_managers.zellij_local import ZellijLayoutGenerator
    
    session_dir = TMP_SERIALIZATION_DIR / session_id
    if not session_dir.exists():
        raise FileNotFoundError(f"Session directory not found: {session_dir}")
    config_file = session_dir / "session_layouts.json"
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    text = config_file.read_text(encoding="utf-8")
    session_layouts = json.loads(text)
    managers = []
    managers_dir = session_dir / "managers"
    if managers_dir.exists():
        manager_files = sorted(managers_dir.glob("manager_*.json"))
        for manager_file in manager_files:
            try:
                text = manager_file.read_text(encoding="utf-8")
                manager_data = json.loads(text)
                manager = ZellijLayoutGenerator(layout_config=manager_data["layout_config"], session_name=manager_data["session_name"])
                manager.layout_path = manager_data["layout_path"]
                managers.append(manager)
            except Exception as e:
                logger.warning(f"Failed to load manager from {manager_file}: {e}")
    logger.info(f"✅ Loaded ZellijLocalManager session from: {session_dir}")
    return session_layouts, managers


def kill_all_sessions(managers: list["ZellijLayoutGenerator"]) -> dict[str, StartResult]:
    """Kill all managed zellij sessions."""
    results: dict[str, StartResult] = {}
    for manager in managers:
        try:
            session_name = manager.session_name
            cmd = f"zellij delete-session --force {session_name}"
            logger.info(f"Killing session '{session_name}'")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            results[session_name] = {"success": result.returncode == 0, "message": "Session killed" if result.returncode == 0 else result.stderr}
        except Exception as e:
            key = getattr(manager, "session_name", None) or f"manager_{managers.index(manager)}"
            results[key] = {"success": False, "error": str(e)}
    return results
