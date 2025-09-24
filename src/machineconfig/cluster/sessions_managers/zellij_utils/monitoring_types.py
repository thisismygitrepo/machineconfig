# TypedDict definitions for better type safety
from typing import NotRequired, TypedDict, Optional

# Import concrete types to replace Any usage
from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig


class ProcessInfo(TypedDict):
    pid: int
    name: str
    cmdline: list[str]
    status: str

class CommandStatus(TypedDict):
    status: str
    running: bool
    processes: list[ProcessInfo]
    command: str
    cwd: str
    tab_name: str
    error: NotRequired[str]
    pid: NotRequired[int]


class SessionStatus(TypedDict):
    session_exists: bool
    zellij_running: bool
    session_name: str
    all_sessions: list[str]
    error: NotRequired[str]


class CommandSummary(TypedDict):
    total_commands: int
    running_commands: int
    stopped_commands: int
    session_healthy: bool


class CommandStatusResult(TypedDict):
    status: str
    running: bool
    processes: list[ProcessInfo]
    command: str
    cwd: str
    tab_name: str
    error: NotRequired[str]
    pid: NotRequired[int]


class ZellijSessionStatus(TypedDict):
    zellij_running: bool
    session_exists: NotRequired[bool]
    session_name: str
    all_sessions: list[str]
    error: NotRequired[str]


class SessionReport(TypedDict):
    session_status: ZellijSessionStatus  # ZellijSessionStatus from zellij_local
    commands_status: dict[str, CommandStatusResult]  # dict[str, CommandStatusResult from zellij_local]  
    summary: CommandSummary


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


class StatusSummary(TypedDict):
    total_commands: int
    running_commands: int
    stopped_commands: int
    session_healthy: bool


class ComprehensiveStatus(TypedDict):
    zellij_session: ZellijSessionStatus
    commands: dict[str, CommandStatusResult]
    summary: StatusSummary