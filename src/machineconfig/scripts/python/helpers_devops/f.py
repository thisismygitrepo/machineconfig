from enum import Enum
import typer
from typing_extensions import Annotated

class OnConflictAction(str, Enum):
    THROW_ERROR            = "throw-error"
    OVERWRITE_SELF_MANAGED = "overwrite-self-managed"
    BACKUP_SELF_MANAGED    = "backup-self-managed"
    OVERWRITE_DEFAULT_PATH = "overwrite-default-path"
    BACKUP_DEFAULT_PATH    = "backup-default-path"

SHORT = {
    "t": OnConflictAction.THROW_ERROR,
    "o": OnConflictAction.OVERWRITE_SELF_MANAGED,
    "b": OnConflictAction.BACKUP_SELF_MANAGED,
    "O": OnConflictAction.OVERWRITE_DEFAULT_PATH,
    "B": OnConflictAction.BACKUP_DEFAULT_PATH,
}

def _parse_on_conflict(v: str | OnConflictAction) -> OnConflictAction:
    if isinstance(v, OnConflictAction):
        return v
    if v in SHORT:
        return SHORT[v]
    try:
        return OnConflictAction(v)
    except ValueError:
        allowed = [e.value for e in OnConflictAction]
        raise typer.BadParameter(
            f"Invalid value {v!r}. Use one of {allowed} or short codes {list(SHORT)}"
        )

def main(
    on_conflict: Annotated[
        OnConflictAction,
        typer.Option(
            "--on-conflict", "-o",
            callback=_parse_on_conflict,
            help="Conflict action. Short: t/o/b/O/B"
        ),
    ] = OnConflictAction.THROW_ERROR,   # <-- default goes here
):
    print(f"Selected: {on_conflict.value}")

if __name__ == "__main__":
    typer.run(main)
