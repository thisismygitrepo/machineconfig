
import typer


def get_app():
    app = typer.Typer(
        name="security-cli",
        help="Security related CLI tools.",
        no_args_is_help=True,
    )


    return app
