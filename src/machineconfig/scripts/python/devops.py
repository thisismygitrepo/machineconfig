
from platform import system
# import subprocess
import crocodile.toolbox as tb


PROGRAM_PATH = tb.P.tmp().joinpath("shells/python_return_command") + (".ps1" if system() == "Windows" else ".sh")


if system() == 'Windows':
    mydict = {
        "update essential repos": "~/code/machineconfig/src/machineconfig/jobs/windows/update_essentials.ps1",
        "install devapps": "~/code/machineconfig/src/machineconfig/setup_windows/devapps.ps1",
        "create symlinks": "~/code/machineconfig/src/machineconfig/setup_windows/symlinks.ps1",

    }
else:
    mydict = {
        "update essential repos": "source ~/code/machineconfig/src/machineconfig/jobs/linux/update_essentials",
        "install devapps": "source <(sudo cat ~/code/machineconfig/src/machineconfig/setup_linux/devapps.sh)",
        "create symlinks": "source ~/code/machineconfig/src/machineconfig/setup_linux/symlinks.sh ",
    }

mydict.update({
    "pull all repos": "",
    "commit all repos": "",
    "push all repos": "",

})


def main():
    PROGRAM_PATH.delete(sure=True, verbose=False)

    for idx, (key, value) in enumerate(mydict.items()):
        print(idx, key, value)
    choice_idx = input("Enter your choice: ")
    choice_key = list(mydict.keys())[int(choice_idx)]
    print(choice_key)
    program = mydict[choice_key]

    if choice_key == "pull all repos":
        from machineconfig.jobs.python.repos import pull_all
        program = pull_all()
    elif choice_key == "push all repos":
        from machineconfig.jobs.python.repos import push_all
        program = push_all()
    elif choice_key == "commit all repos":
        from machineconfig.jobs.python.repos import commit_all
        program = commit_all()
    elif choice_key == "install devapps":
        if system() == "Windows": from machineconfig.jobs.python.python_windows_installers_all import get_installers
        else: from machineconfig.jobs.python.python_linux_installers_all import get_installers
        installers = get_installers()
        installers.list.insert(0, tb.P("all"))
        installers.print(styler=lambda x: x.stem)
        idx = int(input("\nChoose a program: "))
        if idx == 0:
            program1 = "source ~/code/machineconfig/src/machineconfig/setup_linux/devapps.sh"
            program2 = "~/code/machineconfig/src/machineconfig/setup_windows/devapps.ps1"
            program = program1 if system() == "Linux" else program2
        else:
            installers[idx].readit()  # finish the task
            program = "~/.bashrc"  # write an empty program

    # print(f"Executing {program}")
    if system() == 'Windows': PROGRAM_PATH.create(parents_only=True).write_text(program)
    else: PROGRAM_PATH.create(parents_only=True).write_text(f"{program}")


if __name__ == "__main__":
    main()
