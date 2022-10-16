
from platform import system
# import subprocess


if system() == 'Windows':
    mydict = {
        "update essential repos": "~/code/machineconfig/src/machineconfig/jobs/windows/update_essentials.ps1",
        "install devapps": "~/code/machineconfig/src/machineconfig/setup_windows/devapps.ps1",
        "create symlinks": "~/code/machineconfig/src/machineconfig/setup_windows/symlinks.ps1",

    }
else:
    mydict = {
        "update essential repos": "~/code/machineconfig/src/machineconfig/jobs/linux/update_essentials.sh",
        "install devapps": "source <(sudo cat ~/code/machineconfig/src/machineconfig/setup_linux/devapps.sh)",
        "create symlinks": "~/code/machineconfig/src/machineconfig/setup_linux/symlinks.sh ",
    }


def main():
    for idx, (key, value) in enumerate(mydict.items()):
        print(idx, key, value)
    choice = input("Enter your choice: ")
    program = mydict[list(mydict.keys())[int(choice)]]
    print(f"Executing {program}")
    import crocodile.toolbox as tb
    if system() == 'Windows':
        tb.P.tmp().joinpath("shells/python_return_command.ps1").create(parents_only=True).write_text(program)
    else:
        tb.P.tmp().joinpath("shells/python_return_command.sh").create(parents_only=True).write_text(program)


if __name__ == "__main__":
    main()
