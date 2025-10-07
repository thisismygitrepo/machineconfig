
import typer

cli_app = typer.Typer(help="🔄 SELF operations subcommands", no_args_is_help=True)


@cli_app.command()
def update():
    """🔄 UPDATE essential repos"""
    import machineconfig.scripts.python.devops_helpers.devops_update_repos as helper
    helper.main()
@cli_app.command()
def interactive():
    """🤖 INTERACTIVE configuration of machine."""
    from machineconfig.scripts.python.interactive import main
    main()
@cli_app.command()
def status():
    """📊 STATUS of machine, shell profile, apps, symlinks, dotfiles, etc."""
    import machineconfig.scripts.python.devops_helpers.devops_status as helper
    helper.main()
@cli_app.command()
def clone():
    """📋 CLONE machienconfig locally and incorporate to shell profile for faster execution and nightly updates."""
    import platform
    from machineconfig.utils.code import run_shell_script
    from machineconfig.profile.shell import create_default_shell_profile
    if platform.system() == "Windows":
        from machineconfig.setup_windows import MACHINECONFIG
        create_default_shell_profile(method="copy")
    else:
        from machineconfig.setup_linux import MACHINECONFIG
        create_default_shell_profile(method="reference")
    run_shell_script(MACHINECONFIG.read_text(encoding="utf-8"))

@cli_app.command()
def navigate():
    """📚 NAVIGATE command structure with TUI"""
    from machineconfig.scripts.python.devops_navigator import main
    main()

