

import crocodile.environment as env
from src import retrieve_from_onedrive, backup_to_onedrive


def backup_dotfiles(): backup_to_onedrive("~/dotfiles")
def retrieve_dotfiles(): retrieve_from_onedrive("~/dotfiles")


THUNDERBIRD = env.AppData / "Thunderbird" / "Profiles"


def backup_thunderbird(): THUNDERBIRD.search().apply(lambda item: backup_to_onedrive(item))
def retrieve_thunderbird(): THUNDERBIRD.search().apply(lambda item: retrieve_from_onedrive(item))


if __name__ == '__main__':
    pass
