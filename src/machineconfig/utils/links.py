from machineconfig.utils.path_extended import PathExtended, PLike
from machineconfig.utils.accessories import randstr
from rich.console import Console
from rich.panel import Panel
import hashlib
from typing import TypedDict, Literal

console = Console()


class SymlinkResult(TypedDict):
    action: Literal[
        "already_linked",
        "relinking", 
        "fixing_broken_link",
        "identical_files",
        "backing_up_source",
        "backing_up_target", 
        "relinking_to_new_target",
        "moving_to_target",
        "new_link",
        "new_link_and_target",
        "linking",
        "error"
    ]
    details: str


class CopyResult(TypedDict):
    action: Literal[
        "already_linked",
        "relinking",
        "fixing_broken_link", 
        "backing_up_source",
        "backing_up_target",
        "relinking_to_new_target",
        "moving_to_target",
        "new_link",
        "new_link_and_target",
        "copying",
        "error"
    ]
    details: str


def files_are_identical(file1: PathExtended, file2: PathExtended) -> bool:
    """Check if two files are identical by comparing their SHA256 hashes."""
    def get_file_hash(path: PathExtended) -> str:
        hash_sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    try:
        return get_file_hash(file1) == get_file_hash(file2)
    except (OSError, IOError):
        return False


def build_links(target_paths: list[tuple[PLike, str]], repo_root: PLike):
    """Build symboic links from various relevant paths (e.g. data) to `repo_root/links/<name>` to facilitate easy access from
    tree explorer of the IDE.
    """
    target_dirs_filtered: list[tuple[PathExtended, str]] = []
    for a_dir, a_name in target_paths:
        a_dir_obj = PathExtended(a_dir).resolve()
        if not a_dir_obj.exists():
            a_dir_obj.mkdir(parents=True, exist_ok=True)
        target_dirs_filtered.append((a_dir_obj, a_name))

    import git

    repo = git.Repo(repo_root, search_parent_directories=True)
    root_maybe = repo.working_tree_dir
    assert root_maybe is not None
    repo_root_obj = PathExtended(root_maybe)
    tmp_results_root = PathExtended.home().joinpath("tmp_results", "tmp_data", repo_root_obj.name)
    tmp_results_root.mkdir(parents=True, exist_ok=True)
    target_dirs_filtered.append((tmp_results_root, "tmp_results"))

    for a_target_path, a_name in target_dirs_filtered:
        links_path = repo_root_obj.joinpath("links", a_name)
        links_path.symlink_to(target=a_target_path)


def symlink_func(this: PathExtended, to_this: PathExtended, prioritize_to_this: bool) -> SymlinkResult:
    """helper function. creates a symlink from `this` to `to_this`.

    Returns a dict with 'action' and 'details' keys describing what was done.

    this: exists           AND    to_this exists            AND this is a symlink pointing to to_this              ===> Resolution: AUTO: do nothing, already linked correctly.
    this: exists           AND    to_this exists            AND this is a symlink pointing to somewhere else       ===> Resolution: AUTO: delete this symlink, create symlink to to_this
    this: exists           AND    to_this exists            AND this is a concrete path                            ===> Resolution: DANGER: If files are identical (same hash), delete `this` and create symlink to `to_this`. Otherwise, two options: 1) prioritize `this`: to_this is backed up as to_this.orig_<randstr()>, to_this is deleted,  and symlink is created from this to to_this as normal; 2) prioritize `to_this`: `this` is backed up as this.orig_<randstr()>, `this` is deleted, and symlink is created from this to to_this as normal.

    this: exists           AND    to_this doesn't exist     AND this is a symlink pointing to somewhere else       ===> Resolution: AUTO: delete this symlink, create symlink to to_this (touch to_this)
    this: exists           AND    to_this doesn't exist     AND this is a symlink pointing to to_this              ===> Resolution: AUTO: delete this symlink, create symlink to to_this (touch to_this)
    this: exists           AND    to_this doesn't exist     AND this is a concrete path                            ===> Resolution: AUTO: move this to to_this, then create symlink from this to to_this.

    this: doesn't exist    AND    to_this exists                                                                   ===> Resolution: AUTO: create link from this to to_this
    this: doesn't exist    AND    to_this doesn't exist                                                            ===> Resolution: AUTO: create link from this to to_this (touch to_this)

    """
    this = PathExtended(this).expanduser().absolute()
    to_this = PathExtended(to_this).expanduser().absolute()
    action_taken = ""
    details = ""
    
    # Case analysis based on docstring
    if this.exists():
        if to_this.exists():
            if this.is_symlink():
                # Check if symlink already points to correct target
                try:
                    if this.readlink().resolve() == to_this.resolve():
                        # Case: this exists AND to_this exists AND this is a symlink pointing to to_this
                        action_taken = "already_linked"
                        details = "Symlink already correctly points to target"
                        console.print(Panel(f"✅ ALREADY LINKED | {this} ➡️  {to_this}", title="Already Linked", expand=False))
                        return {"action": action_taken, "details": details}
                    else:
                        # Case: this exists AND to_this exists AND this is a symlink pointing to somewhere else
                        action_taken = "relinking"
                        details = "Updated existing symlink to point to new target"
                        console.print(Panel(f"🔄 RELINKING | Updating symlink from {this} ➡️  {to_this}", title="Relinking", expand=False))
                        this.delete(sure=True)
                except OSError:
                    # Broken symlink case
                    action_taken = "fixing_broken_link"
                    details = "Removed broken symlink and will create new one"
                    console.print(Panel(f"🔄 FIXING BROKEN LINK | Fixing broken symlink from {this} ➡️  {to_this}", title="Fixing Broken Link", expand=False))
                    this.delete(sure=True)
            else:
                # Case: this exists AND to_this exists AND this is a concrete path
                if files_are_identical(this, to_this):
                    # Files are identical, just delete this and create symlink
                    action_taken = "identical_files"
                    details = "Files identical, removed source and will create symlink"
                    console.print(Panel(f"🔗 IDENTICAL FILES | Files are identical, deleting {this} and creating symlink to {to_this}", title="Identical Files", expand=False))
                    this.delete(sure=True)
                else:
                    # Files are different, use prioritization logic
                    if prioritize_to_this:
                        # prioritize `to_this`: `this` is backed up, `this` is deleted, symlink created
                        backup_name = f"{this}.orig_{randstr()}"
                        action_taken = "backing_up_source"
                        details = f"Backed up source to {backup_name}, prioritizing target"
                        console.print(Panel(f"📦 BACKING UP | Moving {this} to {backup_name}, prioritizing {to_this}", title="Backing Up", expand=False))
                        this.move(path=backup_name)
                    else:
                        # prioritize `this`: to_this is backed up, to_this is deleted, this content moved to to_this location
                        backup_name = f"{to_this}.orig_{randstr()}"
                        action_taken = "backing_up_target"
                        details = f"Backed up target to {backup_name}, prioritizing source"
                        console.print(Panel(f"📦 BACKING UP | Moving {to_this} to {backup_name}, prioritizing {this}", title="Backing Up", expand=False))
                        to_this.move(path=backup_name)
                        this.move(path=to_this)
        else:
            # to_this doesn't exist
            if this.is_symlink():
                # Case: this exists AND to_this doesn't exist AND this is a symlink (pointing anywhere)
                action_taken = "relinking_to_new_target"
                details = "Removed existing symlink, will create target and new symlink"
                console.print(Panel(f"🔄 RELINKING | Updating symlink from {this} ➡️  {to_this}", title="Relinking", expand=False))
                this.delete(sure=True)
                # Create to_this
                to_this.parent.mkdir(parents=True, exist_ok=True)
                to_this.touch()
            else:
                # Case: this exists AND to_this doesn't exist AND this is a concrete path
                action_taken = "moving_to_target"
                details = "Moved source to target location, will create symlink"
                console.print(Panel(f"📁 MOVING | Moving {this} to {to_this}, then creating symlink", title="Moving", expand=False))
                this.move(path=to_this)
    else:
        # this doesn't exist
        if to_this.exists():
            # Case: this doesn't exist AND to_this exists
            action_taken = "new_link"
            details = "Creating new symlink to existing target"
            console.print(Panel(f"🆕 NEW LINK | Creating new symlink from {this} ➡️  {to_this}", title="New Link", expand=False))
        else:
            # Case: this doesn't exist AND to_this doesn't exist
            action_taken = "new_link_and_target"
            details = "Creating target file and new symlink"
            console.print(Panel(f"🆕 NEW LINK & TARGET | Creating {to_this} and symlink from {this} ➡️  {to_this}", title="New Link & Target", expand=False))
            to_this.parent.mkdir(parents=True, exist_ok=True)
            to_this.touch()
    
    # Create the symlink
    try:
        action_taken = action_taken or "linking"
        details = details or "Creating symlink"
        console.print(Panel(f"🔗 LINKING | Creating symlink from {this} ➡️  {to_this}", title="Linking", expand=False))
        PathExtended(this).symlink_to(target=to_this, verbose=True, overwrite=True)
        return {"action": action_taken, "details": details}
    except Exception as ex:
        action_taken = "error"
        details = f"Failed to create symlink: {str(ex)}"
        console.print(Panel(f"❌ ERROR | Failed at linking {this} ➡️  {to_this}. Reason: {ex}", title="Error", expand=False))
        return {"action": action_taken, "details": details}


def symlink_copy(this: PathExtended, to_this: PathExtended, prioritize_to_this: bool) -> CopyResult:
    this = PathExtended(this).expanduser().absolute()
    to_this = PathExtended(to_this).expanduser().absolute()
    action_taken = ""
    details = ""
    
    if this.exists():
        if to_this.exists():
            if this.is_symlink():
                try:
                    if this.readlink().resolve() == to_this.resolve():
                        action_taken = "already_linked"
                        details = "Symlink already correctly points to target"
                        console.print(Panel(f"✅ ALREADY LINKED | {this} ➡️  {to_this}", title="Already Linked", expand=False))
                        return {"action": action_taken, "details": details}
                    else:
                        action_taken = "relinking"
                        details = "Updated existing symlink to point to new target"
                        console.print(Panel(f"🔄 RELINKING | Updating symlink from {this} ➡️  {to_this}", title="Relinking", expand=False))
                        this.delete(sure=True)
                except OSError:
                    action_taken = "fixing_broken_link"
                    details = "Removed broken symlink and will create new one"
                    console.print(Panel(f"🔄 FIXING BROKEN LINK | Fixing broken symlink from {this} ➡️  {to_this}", title="Fixing Broken Link", expand=False))
                    this.delete(sure=True)
            else:
                if prioritize_to_this:
                    backup_name = f"{this}.orig_{randstr()}"
                    action_taken = "backing_up_source"
                    details = f"Backed up source to {backup_name}, prioritizing target"
                    console.print(Panel(f"📦 BACKING UP | Moving {this} to {backup_name}, prioritizing {to_this}", title="Backing Up", expand=False))
                    this.move(path=backup_name)
                else:
                    backup_name = f"{to_this}.orig_{randstr()}"
                    action_taken = "backing_up_target"
                    details = f"Backed up target to {backup_name}, prioritizing source"
                    console.print(Panel(f"📦 BACKING UP | Moving {to_this} to {backup_name}, prioritizing {this}", title="Backing Up", expand=False))
                    to_this.move(path=backup_name)
                    this.move(path=to_this)
        else:
            if this.is_symlink():
                action_taken = "relinking_to_new_target"
                details = "Removed existing symlink, will create target and new symlink"
                console.print(Panel(f"🔄 RELINKING | Updating symlink from {this} ➡️  {to_this}", title="Relinking", expand=False))
                this.delete(sure=True)
                to_this.parent.mkdir(parents=True, exist_ok=True)
                to_this.touch()
            else:
                action_taken = "moving_to_target"
                details = "Moved source to target location, will copy"
                console.print(Panel(f"📁 MOVING | Moving {this} to {to_this}, then copying", title="Moving", expand=False))
                this.move(path=to_this)
    else:
        if to_this.exists():
            action_taken = "new_link"
            details = "Copying existing target to source location"
            console.print(Panel(f"🆕 NEW LINK | Copying {to_this} to {this}", title="New Link", expand=False))
        else:
            action_taken = "new_link_and_target"
            details = "Creating target file and copying to source"
            console.print(Panel(f"🆕 NEW LINK & TARGET | Creating {to_this} and copying to {this}", title="New Link & Target", expand=False))
            to_this.parent.mkdir(parents=True, exist_ok=True)
            to_this.touch()
    
    try:
        action_taken = action_taken or "copying"
        details = details or "Copying file"
        console.print(Panel(f"📋 COPYING | Copying {to_this} to {this}", title="Copying", expand=False))
        to_this.copy(path=this, overwrite=True, verbose=True)
        return {"action": action_taken, "details": details}
    except Exception as ex:
        action_taken = "error"
        details = f"Failed to copy file: {str(ex)}"
        console.print(Panel(f"❌ ERROR | Failed at copying {to_this} to {this}. Reason: {ex}", title="Error", expand=False))
        return {"action": action_taken, "details": details}
