from machineconfig.utils.path_reduced import P as PathExtended, PLike
from machineconfig.utils.utils2 import randstr
from rich.console import Console
from rich.panel import Panel


console = Console()


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

def symlink_func(this: PathExtended, to_this: PathExtended, prioritize_to_this: bool=True):
    """helper function. creates a symlink from `this` to `to_this`.
    What can go wrong?
    depending on this and to_this existence, one will be prioretized depending on overwrite value.
    True means this will potentially be overwritten (depending on whether to_this exists or not)
    False means to_this will potentially be overwittten."""
    this = PathExtended(this).expanduser().absolute()
    to_this = PathExtended(to_this).expanduser().absolute()
    if this.is_symlink(): this.delete(sure=True)  # delete if it exists as symblic link, not a concrete path.
    if this.exists():  # this is a problem. It will be resolved via `overwrite`
        if prioritize_to_this is True:  # it *can* be deleted, but let's look at target first.
            if to_this.exists():  # this exists, to_this as well. to_this is prioritized.
                this.append(f".orig_{randstr()}", inplace=True)  # rename is better than deletion
            else: this.move(path=to_this)  # this exists, to_this doesn't. to_this is prioritized.
        elif prioritize_to_this is False:  # don't sacrefice this, sacrefice to_this.
            if to_this.exists(): this.move(path=to_this, overwrite=True)  # this exists, to_this as well, this is prioritized.   # now we are readly to make the link
            else: this.move(path=to_this)  # this exists, to_this doesn't, this is prioritized.
    else:  # this doesn't exist.
        if not to_this.exists():
            to_this.parent.mkdir(parents=True, exist_ok=True)
            to_this.touch()  # we have to touch it (file) or create it (folder)
    try:
        console.print(Panel(f"🔗 LINKING | Creating symlink from {this} ➡️  {to_this}", title="Linking", expand=False))
        PathExtended(this).symlink_to(target=to_this, verbose=True, overwrite=True)
    except Exception as ex:
        console.print(Panel(f"❌ ERROR | Failed at linking {this} ➡️  {to_this}. Reason: {ex}", title="Error", expand=False))

def symlink_copy(this: PathExtended, to_this: PathExtended, prioritize_to_this: bool=True):
    this = PathExtended(this).expanduser().absolute()
    to_this = PathExtended(to_this).expanduser().absolute()
    if this.is_symlink(): this.delete(sure=True)  # delete if it exists as symblic link, not a concrete path.
    if this.exists():  # this is a problem. It will be resolved via `overwrite`
        if prioritize_to_this is True:  # it *can* be deleted, but let's look at target first.
            if to_this.exists():  # this exists, to_this as well. to_this is prioritized.
                this.append(f".orig_{randstr()}", inplace=True)  # rename is better than deletion
            else: this.move(path=to_this)  # this exists, to_this doesn't. to_this is prioritized.
        elif prioritize_to_this is False:  # don't sacrefice this, sacrefice to_this.
            if to_this.exists(): this.move(path=to_this, overwrite=True)  # this exists, to_this as well, this is prioritized.   # now we are readly to make the link
            else: this.move(path=to_this)  # this exists, to_this doesn't, this is prioritized.
    else:  # this doesn't exist.
        if not to_this.exists():
            to_this.parent.mkdir(parents=True, exist_ok=True)
            to_this.touch()  # we have to touch it (file) or create it (folder)
    try:
        console.print(Panel(f"📋 COPYING | Copying {to_this} to {this}", title="Copying", expand=False))
        to_this.copy(path=this, overwrite=True, verbose=True)
    except Exception as ex:
        console.print(Panel(f"❌ ERROR | Failed at copying {to_this} to {this}. Reason: {ex}", title="Error", expand=False))
