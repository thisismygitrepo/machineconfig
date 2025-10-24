import json
import uuid
import logging
import shutil
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def generate_session_id() -> str:
    return str(uuid.uuid4())[:8]


def save_json_file(file_path: Path, data: dict[str, Any] | list[Any], description: str) -> None:
    text = json.dumps(data, indent=2, ensure_ascii=False)
    file_path.write_text(text, encoding="utf-8")
    logger.debug(f"Saved {description} to {file_path}")


def load_json_file(file_path: Path, description: str) -> dict[str, Any] | list[Any]:
    if not file_path.exists():
        raise FileNotFoundError(f"{description} not found: {file_path}")
    text = file_path.read_text(encoding="utf-8")
    return json.loads(text)


def list_saved_sessions_in_dir(serialization_dir: Path) -> list[str]:
    if not serialization_dir.exists():
        return []
    sessions = []
    for item in serialization_dir.iterdir():
        if item.is_dir() and (item / "metadata.json").exists():
            sessions.append(item.name)
    return sorted(sessions)


def delete_session_dir(session_dir: Path, session_id: str) -> bool:
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


def ensure_session_dir_exists(session_dir: Path) -> None:
    session_dir.mkdir(parents=True, exist_ok=True)
