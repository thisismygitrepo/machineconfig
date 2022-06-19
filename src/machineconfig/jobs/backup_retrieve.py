

import crocodile.environment as env
from machine_setup.jobs.utils import retrieve as retrieve_func, backup as backup_func


def backup_dotfiles(): backup_func("~/dotfiles")
def retrieve_dotfiles(): retrieve_func(source_file="dotfiles_encrypted.zip", target_folder="~")
def backup_thunderbird(): backup_func(env.AppData / "Thunderbird" / "Profiles" / "h7omvr4i.default-release")
def retrieve_thunderbird(): retrieve_func(source_file="thunderbird_encrypted.zip", target_folder=env.AppData / "Thunderbird" / "Profiles")


if __name__ == '__main__':
    pass
