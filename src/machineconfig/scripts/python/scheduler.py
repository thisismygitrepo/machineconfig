
"""Task scheduler
"""

from crocodile.file_management import P, Read
# from crocodile.meta import Scheduler


ROOT = P.home().joinpath("dotfiles/config/scheduler/tasks.ini")

tasks = Read.ini(ROOT)

for a_section in tasks.sections():
    a_task = tasks[a_section]


if __name__ == "__main__":
    pass
