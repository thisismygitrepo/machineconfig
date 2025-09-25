
from typing import NotRequired, TypedDict, Optional
from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig


class ProcessInfo(TypedDict):
    pid: int
    name: str
    cmdline: list[str]
    status: str
    cmdline_str: NotRequired[str]
    create_time: NotRequired[float]
    is_direct_command: NotRequired[bool]
    verified_alive: NotRequired[bool]
    memory_mb: NotRequired[float]


class CommandStatus(TypedDict):
    status: str                   # e.g. running | not_running | unknown | error
    running: bool                 # Convenience boolean
    processes: list[ProcessInfo]  # Matching processes (can be empty)
    command: str                  # Original command string ('' if unknown)
    tab_name: str                 # Tab identifier
    # Optional / contextual fields
    cwd: NotRequired[str]
    error: NotRequired[str]
    pid: NotRequired[int]
    remote: NotRequired[str]
    check_timestamp: NotRequired[str | float]
    method: NotRequired[str]
    raw_output: NotRequired[str]
    verification_method: NotRequired[str]
class CommandSummary(TypedDict):
    total_commands: int
    running_commands: int
    stopped_commands: int
    session_healthy: bool

class ZellijSessionStatus(TypedDict):
    zellij_running: bool
    session_exists: bool
    session_name: str
    all_sessions: list[str]
    error: NotRequired[str]


class SessionReport(TypedDict):
    session_status: ZellijSessionStatus  # ZellijSessionStatus from zellij_local
    commands_status: dict[str, CommandStatus]  # dict[str, CommandStatus from zellij_local]
    summary: CommandSummary
class ComprehensiveStatus(TypedDict):
    zellij_session: ZellijSessionStatus
    commands: dict[str, CommandStatus]
    summary: CommandSummary
class SessionMetadata(TypedDict):
    session_name_prefix: str
    created_at: str
    num_managers: int
    sessions: list[str]
    manager_type: str
class ManagerData(TypedDict):
    session_name: Optional[str]
    layout_config: Optional[LayoutConfig]  # Will be LayoutConfig from layout_types
    layout_path: Optional[str]
class ActiveSessionInfo(TypedDict):
    session_name: str
    is_active: bool
    tab_count: int
    tabs: list[str]


class GlobalSummary(TypedDict):
    total_sessions: int
    healthy_sessions: int
    unhealthy_sessions: int
    total_commands: int
    running_commands: int
    stopped_commands: int
    all_sessions_healthy: bool
    all_commands_running: bool


class StartResult(TypedDict):
    success: bool
    message: NotRequired[str]
    error: NotRequired[str]
class StatusRow(TypedDict):
    session: str
    tab: str
    running: bool
    command: str
    processes: int


