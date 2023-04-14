
import crocodile.toolbox as tb
from machineconfig.utils.utils import display_options, PROGRAM_PATH, get_current_ve, choose_ssh_host
# https://github.com/pallets/click combine with fire. Consider
# https://github.com/ceccopierangiolieugenio/pyTermTk for display_options build TUI
# https://github.com/chriskiehl/Gooey build commandline interface
import inspect


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=str, help="The directory containing the jobs", default=".")
    # optional flag for interactivity
    parser.add_argument("--interactive", "-i", action="store_true", help="Whether to run the job interactively")
    parser.add_argument("--debug", "-d", action="store_true", help="debug")
    parser.add_argument("--remote", "-r", action="store_true", help="launch on a remote machine")
    parser.add_argument("--main", "-m", action="store_true", help="launch the main file")
    args = parser.parse_args()
    jobs_dir = args.path
    jobs_dir = tb.P(jobs_dir).expanduser().absolute()
    print(f"Seaching recursively for all python file in directory `{jobs_dir}`")
    py_files = jobs_dir.search("*.py", not_in=["__init__.py"], r=True).to_list()
    choice_file = display_options(msg="Choose a file to run", options=py_files, fzf=True, multi=False)

    if args.interactive is False: exe = "python"
    else: exe = "ipython -i"
    try:
        ve_name = get_current_ve()
        exe = f". activate_ve {ve_name}; {exe}"
    except NotImplementedError:
        print(f"Failed to detect virtual enviroment name.")
        pass
    if args.debug: command = f"{exe} -m pudb {choice_file} "  # TODO: functions not supported yet in debug mode.
    elif args.main: command = f"{exe} {choice_file}"
    else:
        module, choice_function = choose_function(choice_file)
        if choice_function != "RUN AS MAIN":
            kgs1, kgs2 = interactively_run_function(module[choice_function])
            command = f"{exe} -m fire {choice_file} {choice_function} " + " ".join([f"--{k} {v}" for k, v in kgs1.items()])
        else: command = f"{exe} {choice_file} "
        if args.remote: return run_on_remote(choice_file, args=args)
    print("\n", command, "\n\n\n")
    PROGRAM_PATH.write_text(command)


def choose_function(file_path):
    print(f"Loading {file_path} ...")
    module = tb.P(file_path).readit()
    module: tb.Struct
    module = module.filter(lambda k, v: "function" in str(type(v)))
    module.print()
    options = module.apply(lambda k, v: f"{k} -- {type(v)} {tb.Display.get_repr(v.__doc__, limit=150) if v.__doc__ is not None else 'No docs for this.'}").to_list()
    main_option = f"RUN AS MAIN -- {tb.Display.get_repr(module.__doc__, limit=150) if module.__doc__ is not None else 'No docs for this.'}"
    options.append(main_option)
    choice_function = display_options(msg="Choose a function to run", options=options, fzf=True, multi=False)
    choice_function = choice_function.split(' -- ')[0]
    return module, choice_function


def interactively_run_function(func):
    sig = inspect.signature(func)
    params = list(sig.parameters.values())
    args = []
    kwargs = {}
    for param in params:
        if param.annotation is not inspect.Parameter.empty: hint = f" ({param.annotation.__name__})"
        else: hint = ""
        if param.default is not inspect.Parameter.empty:
            default = param.default
            value = input(f"Please enter a value for argument `{param.name}` (type = {hint}) (default = {default}) : ")
            if value == "": value = default
        else: value = input(f"Please enter a value for argument `{param.name}` (type = {hint}) : ")
        try:
            if param.annotation is not inspect.Parameter.empty: value = param.annotation(value)
        except (TypeError, ValueError): raise ValueError(f"Invalid input: {value} is not of type {param.annotation}")
        if param.kind == inspect.Parameter.KEYWORD_ONLY: kwargs[param.name] = value
        else: args.append((param.name, value))
    args_to_kwargs = dict(args)
    return args_to_kwargs, kwargs


def run_on_remote(func, args):
    host = choose_ssh_host(multi=False)
    from crocodile.cluster.remote_machine import RemoteMachine, RemoteMachineConfig
    config = RemoteMachineConfig(copy_repo=True, update_repo=False, update_essential_repos=True,
                                 notify_upon_completion=True, ssh_params=dict(host=host),
                                 # to_email=None, email_config_name='enaut',
                                 data=[],
                                 ipython=False, interactive=args.interactive, pdb=False, pudb=args.debug, wrap_in_try_except=False,
                                 transfer_method="sftp")
    m = RemoteMachine(func=func, func_kwargs=None, config=config)
    m.run()


if __name__ == '__main__':
    main()

