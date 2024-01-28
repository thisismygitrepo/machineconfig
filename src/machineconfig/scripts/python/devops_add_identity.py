
"""ID
"""


# from platform import system
from crocodile.file_management import P
from machineconfig.utils.utils import display_options


def main():
    private_keys = P.home().joinpath(".ssh").search("*.pub").apply(lambda x: x.with_name(x.stem)).filter(lambda x: x.exists())
    choice = display_options(msg="Path to private key to be used when ssh'ing: ", options=private_keys.apply(str).list + ["I have the path to the key file", "I want to paste the key itself"])
    if choice == "I have the path to the key file": path_to_key = P(input("Input path here: ")).expanduser().absolute()
    elif choice == "I want to paste the key itself": path_to_key = P.home().joinpath(f".ssh/{input('file name (default: my_pasted_key): ') or 'my_pasted_key'}").write_text(input("Paste the private key here: "))
    elif isinstance(choice, str): path_to_key = P(choice)
    else: raise NotImplementedError(f"Choice {choice} not supported")
    txt = f"IdentityFile {path_to_key.collapseuser().as_posix()}"  # adds this id for all connections, no host specified.
    config_path = P.home().joinpath(".ssh/config")
    if config_path.exists(): config_path.modify_text(txt_search=txt, txt_alt=txt, replace_line=True, notfound_append=True, prepend=True)  # note that Identity line must come on top of config file otherwise it won't work, hence `prepend=True`
    else: config_path.write_text(txt)
    program = f"echo 'Finished adding identity to ssh config file. {'*'*50} Consider reloading config file.'"
    return program


if __name__ == '__main__':
    pass
