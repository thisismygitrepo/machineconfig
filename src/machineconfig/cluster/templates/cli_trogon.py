
# """Trogon
# """

# import click
# from trogon import tui
# from typing import Any


# @tui()
# @click.command()
# @click.option('--description', prompt="Description of the job: ", default=f"Description of running func on remotes", help="Write something that describes what this job is about.")
# @click.option('--update_repo', prompt="Update repo: ", default=False, help="Update the repo on the remote machine.")
# @click.pass_context
# def get_choices(ctx: Any, description: str, update_repo: bool):  # type: ignore
#     return ctx


# if __name__ == '__main__':
#     res = get_choices(standalone_mode=False)  # type: ignore
#     print(res)
