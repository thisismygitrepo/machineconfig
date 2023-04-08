
import crocodile.toolbox as tb
from machineconfig.utils.utils import display_options, PROGRAM_PATH, get_current_ve
# https://github.com/pallets/click combine with fire. Consider
# https://github.com/ceccopierangiolieugenio/pyTermTk for display_options build TUI
import inspect


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=str, help="The directory containing the jobs", default=".")
    # optional flag for interactivity
    parser.add_argument("--interactive", "-i", action="store_true", help="Whether to run the job interactively")
    parser.add_argument("--debug", "-d", action="store_true", help="debug")
    # add debugger option
    args = parser.parse_args()
    get_command(jobs_dir=args.path, interactive=args.interactive, debug=args.debug)


def get_command(jobs_dir, interactive=False, debug=False):
    jobs_dir = tb.P(jobs_dir).expanduser().absolute()
    print(f"Seaching recursively for all python file in directory `{jobs_dir}`")
    py_files = jobs_dir.search("*.py", not_in=["__init__.py"], r=True).to_list()
    choice_file = display_options(msg="Choose a file to run", options=py_files, fzf=True, multi=False)
    print(f"Loading {choice_file} ...")
    module = tb.P(choice_file).readit()
    module: tb.Struct
    module = module.filter(lambda k, v: "function" in str(type(v)))
    module.print()
    if interactive is False: exe = "python"
    else: exe = "ipython -i"
    try:
        ve_name = get_current_ve()
        exe = f". activate_ve {ve_name}; {exe}"
    except NotImplementedError:
        print(f"Failed to detect virtual enviroment name.")
        pass

    if debug:
        command = f"{exe} -m pudb {choice_file} "
    else:
        options = module.apply(lambda k,v: f"{k} -- {type(v)} {tb.Display.get_repr(v.__doc__, limit=150) if v.__doc__ is not None else 'No docs for this.'}").to_list()
        main_option = "RUN AS MAIN"
        options.append(main_option)
        choice_function = display_options(msg="Choose a function to run", options=options, fzf=True, multi=False)
        if choice_function != main_option:
            kgs1, kgs2 = interactively_run_function(module[choice_function.split(' -- ')[0]])
            command = f"{exe} -m fire {choice_file} {choice_function} " + " ".join([f"--{k} {v}" for k, v in kgs1.items()])
        else:
            command = f"{exe} {choice_file} "
    print(command)
    PROGRAM_PATH.write_text(command)


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
        else:
            value = input(f"Please enter a value for argument `{param.name}` (type = {hint}) : ")
        try:
            if param.annotation is not inspect.Parameter.empty:
                value = param.annotation(value)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid input: {value} is not of type {param.annotation}")
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            kwargs[param.name] = value
        else:
            args.append((param.name, value))
    args_to_kwargs = dict(args)
    return args_to_kwargs, kwargs


if __name__ == '__main__':
    main()
