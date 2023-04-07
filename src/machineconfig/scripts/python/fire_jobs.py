
import crocodile.toolbox as tb
from machineconfig.utils.utils import display_options, PROGRAM_PATH
# https://github.com/pallets/click combine with fire. Consider
# https://github.com/ceccopierangiolieugenio/pyTermTk for display_options build TUI
import inspect


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("jobs_dir", type=str, help="The directory containing the jobs")
    # optional flag for interactivity
    parser.add_argument("--interactive", "-i", action="store_true", help="Whether to run the job interactively")
    parser.add_argument("--debug", "-d", action="store_true", help="debug")
    # add debugger option
    args = parser.parse_args()
    get_command(jobs_dir=args.jobs_dir, interactive=args.interactive, debug=args.debug)


def get_command(jobs_dir, interactive=False, debug=False):
    py_files = tb.P(jobs_dir).search("*.py", not_in=["__init__.py"], r=True).to_list()
    choice_file = display_options(msg="Choose a file to run", options=py_files, fzf=True, multi=False)
    module = tb.P(choice_file).readit()
    module: tb.Struct
    module = module.filter(lambda k, v: type(v) not in {str, None, dict} and v is not None and "module" not in str(type(v)))
    module.print()
    if interactive is False: exe = "python"
    else: exe = "ipython -i"
    if debug:
        command = f"{exe} -m pudb {choice_file} "
    else:
        choice_function = display_options(msg="Choose a function to run", options=module.keys().to_list(), fzf=True, multi=False)
        kgs1, kgs2 = interactively_run_function(module[choice_function])
        command = f"{exe} -m fire {choice_file} {choice_function} " + " ".join([f"--{k} {v}" for k, v in kgs1.items()])
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
