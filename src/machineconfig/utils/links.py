from machineconfig.utils.path_reduced import PathExtended as PathExtended, PLike
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


def symlink_func(this: PathExtended, to_this: PathExtended, prioritize_to_this: bool):
    """helper function. creates a symlink from `this` to `to_this`.

    this: exists           AND    to_this exists            AND this is a symlink pointing to to_this              ===> Resolution: AUTO: do nothing, already linked correctly.
    this: exists           AND    to_this exists            AND this is a symlink pointing to somewhere else       ===> Resolution: AUTO: delete this symlink, create symlink to to_this
    this: exists           AND    to_this exists            AND this is a concrete path                            ===> Resolution: DANGER: require user input to decide (param prioritize_to_this). Give two options: 1) prioritize `this`: to_this is backed up as to_this.orig_<randstr()>, to_this is deleted,  and symlink is created from this to to_this as normal; 2) prioritize `to_this`: `this` is backed up as this.orig_<randstr()>, `this` is deleted, and symlink is created from this to to_this as normal.

    this: exists           AND    to_this doesn't exist     AND this is a symlink pointing to somewhere else       ===> Resolution: AUTO: delete this symlink, create symlink to to_this (touch to_this)
    this: exists           AND    to_this doesn't exist     AND this is a symlink pointing to to_this              ===> Resolution: AUTO: delete this symlink, create symlink to to_this (touch to_this)
    this: exists           AND    to_this doesn't exist     AND this is a concrete path                            ===> Resolution: AUTO: move this to to_this, then create symlink from this to to_this.

    this: doesn't exist    AND    to_this exists                                                                   ===> Resolution: AUTO: create link from this to to_this
    this: doesn't exist    AND    to_this doesn't exist                                                            ===> Resolution: AUTO: create link from this to to_this (touch to_this)

    """
    this = PathExtended(this).expanduser().absolute()
    to_this = PathExtended(to_this).expanduser().absolute()
    # Case analysis based on docstring
    if this.exists():
        if to_this.exists():
            if this.is_symlink():
                # Check if symlink already points to correct target
                try:
                    if this.readlink().resolve() == to_this.resolve():
                        # Case: this exists AND to_this exists AND this is a symlink pointing to to_this
                        console.print(Panel(f"✅ ALREADY LINKED | {this} ➡️  {to_this}", title="Already Linked", expand=False))
                        return
                    else:
                        # Case: this exists AND to_this exists AND this is a symlink pointing to somewhere else
                        console.print(Panel(f"🔄 RELINKING | Updating symlink from {this} ➡️  {to_this}", title="Relinking", expand=False))
                        this.delete(sure=True)
                except OSError:
                    # Broken symlink case
                    console.print(Panel(f"🔄 FIXING BROKEN LINK | Fixing broken symlink from {this} ➡️  {to_this}", title="Fixing Broken Link", expand=False))
                    this.delete(sure=True)
            else:
                # Case: this exists AND to_this exists AND this is a concrete path
                if prioritize_to_this:
                    # prioritize `to_this`: `this` is backed up, `this` is deleted, symlink created
                    backup_name = f"{this}.orig_{randstr()}"
                    console.print(Panel(f"📦 BACKING UP | Moving {this} to {backup_name}, prioritizing {to_this}", title="Backing Up", expand=False))
                    this.move(path=backup_name)
                else:
                    # prioritize `this`: to_this is backed up, to_this is deleted, this content moved to to_this location
                    backup_name = f"{to_this}.orig_{randstr()}"
                    console.print(Panel(f"📦 BACKING UP | Moving {to_this} to {backup_name}, prioritizing {this}", title="Backing Up", expand=False))
                    to_this.move(path=backup_name)
                    this.move(path=to_this)
        else:
            # to_this doesn't exist
            if this.is_symlink():
                # Case: this exists AND to_this doesn't exist AND this is a symlink (pointing anywhere)
                console.print(Panel(f"🔄 RELINKING | Updating symlink from {this} ➡️  {to_this}", title="Relinking", expand=False))
                this.delete(sure=True)
                # Create to_this
                to_this.parent.mkdir(parents=True, exist_ok=True)
                to_this.touch()
            else:
                # Case: this exists AND to_this doesn't exist AND this is a concrete path
                console.print(Panel(f"📁 MOVING | Moving {this} to {to_this}, then creating symlink", title="Moving", expand=False))
                this.move(path=to_this)
    else:
        # this doesn't exist
        if to_this.exists():
            # Case: this doesn't exist AND to_this exists
            console.print(Panel(f"🆕 NEW LINK | Creating new symlink from {this} ➡️  {to_this}", title="New Link", expand=False))
        else:
            # Case: this doesn't exist AND to_this doesn't exist
            console.print(Panel(f"🆕 NEW LINK & TARGET | Creating {to_this} and symlink from {this} ➡️  {to_this}", title="New Link & Target", expand=False))
            to_this.parent.mkdir(parents=True, exist_ok=True)
            to_this.touch()
    # Create the symlink
    try:
        console.print(Panel(f"🔗 LINKING | Creating symlink from {this} ➡️  {to_this}", title="Linking", expand=False))
        PathExtended(this).symlink_to(target=to_this, verbose=True, overwrite=True)
    except Exception as ex:
        console.print(Panel(f"❌ ERROR | Failed at linking {this} ➡️  {to_this}. Reason: {ex}", title="Error", expand=False))


def symlink_copy(this: PathExtended, to_this: PathExtended, prioritize_to_this: bool):
    this = PathExtended(this).expanduser().absolute()
    to_this = PathExtended(to_this).expanduser().absolute()
    if this.exists():
        if to_this.exists():
            if this.is_symlink():
                try:
                    if this.readlink().resolve() == to_this.resolve():
                        console.print(Panel(f"✅ ALREADY LINKED | {this} ➡️  {to_this}", title="Already Linked", expand=False))
                        return
                    else:
                        console.print(Panel(f"🔄 RELINKING | Updating symlink from {this} ➡️  {to_this}", title="Relinking", expand=False))
                        this.delete(sure=True)
                except OSError:
                    console.print(Panel(f"🔄 FIXING BROKEN LINK | Fixing broken symlink from {this} ➡️  {to_this}", title="Fixing Broken Link", expand=False))
                    this.delete(sure=True)
            else:
                if prioritize_to_this:
                    backup_name = f"{this}.orig_{randstr()}"
                    console.print(Panel(f"📦 BACKING UP | Moving {this} to {backup_name}, prioritizing {to_this}", title="Backing Up", expand=False))
                    this.move(path=backup_name)
                else:
                    backup_name = f"{to_this}.orig_{randstr()}"
                    console.print(Panel(f"📦 BACKING UP | Moving {to_this} to {backup_name}, prioritizing {this}", title="Backing Up", expand=False))
                    to_this.move(path=backup_name)
                    this.move(path=to_this)
        else:
            if this.is_symlink():
                console.print(Panel(f"🔄 RELINKING | Updating symlink from {this} ➡️  {to_this}", title="Relinking", expand=False))
                this.delete(sure=True)
                to_this.parent.mkdir(parents=True, exist_ok=True)
                to_this.touch()
            else:
                console.print(Panel(f"📁 MOVING | Moving {this} to {to_this}, then copying", title="Moving", expand=False))
                this.move(path=to_this)
    else:
        if to_this.exists():
            console.print(Panel(f"🆕 NEW LINK | Copying {to_this} to {this}", title="New Link", expand=False))
        else:
            console.print(Panel(f"🆕 NEW LINK & TARGET | Creating {to_this} and copying to {this}", title="New Link & Target", expand=False))
            to_this.parent.mkdir(parents=True, exist_ok=True)
            to_this.touch()
    try:
        console.print(Panel(f"📋 COPYING | Copying {to_this} to {this}", title="Copying", expand=False))
        to_this.copy(path=this, overwrite=True, verbose=True)
    except Exception as ex:
        console.print(Panel(f"❌ ERROR | Failed at copying {to_this} to {this}. Reason: {ex}", title="Error", expand=False))
