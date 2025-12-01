

def get_read_python_file_pycode(path: str, title: str):
    from pathlib import Path
    print("Reading code from path:", path)
    pycode = Path(path).read_text(encoding="utf-8")
    pycode = pycode.split("except Exception: print(pycode)")[2]
    try:
        # from rich.text import Text
        from rich.panel import Panel
        from rich.console import Console
        from rich.syntax import Syntax
        console = Console()
        if pycode.strip() != "":
            console.print(Panel(Syntax(pycode, lexer="python"), title=title), style="bold red")
    except Exception: print(pycode)


def get_read_data_pycode(path: str):
    from rich.panel import Panel
    from rich.text import Text
    from rich.console import Console
    from pathlib import Path
    console = Console()
    p = Path(path).absolute()
    try:
        from machineconfig.utils.files.read import Read
        from machineconfig.utils.accessories import pprint
        dat = Read.read(p)
        if isinstance(dat, dict):
            panel_title = f"📄 File Data: {p.name}"
            console.print(Panel(Text(str(dat), justify="left"), title=panel_title, expand=False))
            pprint(dat, p.name)
        else:
            panel_title = f"📄 Successfully read the file: {p.name}"
            console.print(Panel(Text(str(dat), justify="left"), title=panel_title, expand=False))
    except Exception as e:
        error_message = f'''❌ ERROR READING FILE\nFile: {p.name}\nError: {e}'''
        console.print(Panel(Text(error_message, justify="left"), title="Error", expand=False, border_style="red"))
