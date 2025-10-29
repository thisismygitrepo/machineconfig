"""Ascii art
"""

import os
import random
import textwrap
import subprocess
from pathlib import Path
import tempfile
import platform
from typing import Optional, Literal

# https://github.com/sepandhaghighi/art


BOX_OR_CHAR = Literal['boxes', 'cowsay']


class ArtLib:
    @staticmethod
    def cowsay(text: str):
        import cowsay
        char = random.choice(cowsay.char_names)
        return cowsay.get_output_string(char, text=text)


class BoxStyles:
    language = ['ada-box', 'caml', 'boxquote', 'stone', 'tex-box', 'shell', 'simple', 'c', 'cc', 'html']
    scene = ['whirly', 'xes', 'columns', 'parchment', 'scroll', 'scroll-akn', 'diamonds', 'headline', 'nuke', 'spring', 'stark1']  # , 'important3'
    character = ['capgirl', 'cat', 'boy', 'girl', 'dog', 'mouse', 'santa', 'face', 'ian_jones', 'peek', 'unicornsay']


class CowStyles:
    eyes = ['-b', '-d', '-g', '-h', '-l', '-L', '-n', '-N', '-p', '-s', '-t', '-w', '-y']
    # this one for the package installed with sudo apt install cowsay and is located at /usr/games/cowsay. See cowsay -l
    figures = ['apt', 'bunny', 'cheese', 'cock', 'cower', 'daemon', 'default', 'dragon',
               'dragon-and-cow', 'duck', 'elephant', 'elephant-in-snake', 'eyes', 'fox', 'ghostbusters',
               'gnu', 'kangaroo', 'kiss', 'milk',
               'moose', 'pony', 'pony-smaller', 'sheep', 'skeleton', 'snowman', 'stegosaurus',  # 'suse',
               'three-eyes', 'turkey', 'turtle', 'tux', 'unipony', 'unipony-smaller', 'vader', 'vader']  # 'hellokitty' 'mech-and-cow'  # 'moofasa', 'stimpy', 'calvin', , 'ren', 'koala', 'flaming-sheep' , 'bud-frogs' , 'kosh' , 'luke-koala'


FIGLET_FONTS = ['banner', 'big', 'standard']

FIGJS_FONTS = ['3D Diagonal', '3D-ASCII', '4Max', '5 Line Oblique', 'Acrobatic', 'ANSI Regular', 'ANSI Shadow',
               'Avatar', 'Banner', 'Banner3-D', 'Banner4',
               'Basic', 'Big Money-ne', 'Big Money-nw', 'Big Money-se', 'Big Money-sw', 'Big', 'Bloody', 'Bolger', 'Braced', 'Bright',
               'DOS Rebel',
               'Elite', 'Epic', 'Flower Power',
               'Fraktur',  # 'Isometric4'. 'AMC Tubes', 'Banner3', Alligator2
               'Star Wars',
               'Sub-Zero', 'The Edge', 'USA Flag', 'Varsity', "Doom"
               ]  # too large  Crazy 'Sweet', 'Electronic', 'Swamp Land', Crawford, Alligator


def get_art(comment: Optional[str] = None, artlib: Optional[BOX_OR_CHAR] = None, style: Optional[str] = None, super_style: str = 'scene', prefix: str = ' ', file: Optional[str] = None, verbose: bool = True):
    """ takes in a comment and does the following wrangling:
    * text => figlet font => boxes => lolcat
    * text => cowsay => lolcat
    """
    if comment is None:
        try:
            comment = subprocess.run("fortune", shell=True, capture_output=True, text=True, check=True).stdout
        except Exception:
            comment = "machineconfig"
    if artlib is None: artlib = random.choice(['boxes', 'cowsay'])
    to_file = '' if not file else f'> {file}'
    if artlib == 'boxes':
        if style is None: style = random.choice(BoxStyles.__dict__[super_style or random.choice(['language', 'scene', 'character'])])
        fonting = f'figlet -f {random.choice(FIGLET_FONTS)}'
        cmd = f"""echo "{comment}" | {fonting} | boxes -d {style} {to_file}"""
    else:
        if style is None: style = random.choice(CowStyles.figures)
        cmd = f"""echo "{comment}" | /usr/games/cowsay -f {style} {to_file}"""
    try:
        res = subprocess.run(cmd, text=True, capture_output=True, shell=True, check=True).stdout
    except subprocess.CalledProcessError as ex:
        print(ex)
        return ""
    res = textwrap.indent(res, prefix=prefix)
    if verbose:
        print(f'Using style: {style} from {artlib}', '\n' * 3)
        print(f'{cmd=}')
        print('Results:\n', res)
    return res


def font_box_color(logo: str):
    font = random.choice(FIGJS_FONTS)
    # print(f"{font}\n")
    box_style = random.choice(['whirly', 'xes', 'columns', 'parchment', 'scroll', 'scroll-akn', 'diamonds', 'headline', 'nuke', 'spring', 'stark1'])
    _cmd = f'figlet -f "{font}" "{logo}" | boxes -d "{box_style}" | lolcatjs'
    # print(_cmd)
    os.system(_cmd)  # | lolcat
    # print("after")


def character_color(logo: str):
    assert platform.system() == 'Windows', 'This function is only for Windows.'
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(ArtLib.cowsay(logo))
        _new_art = f.name
    os.system(f'type {_new_art} | lolcatjs')  # | lolcat


def character_or_box_color(logo: str):
    assert platform.system() in {'Linux', 'Darwin'}, 'This function is only for Linux and macOS.'
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        _new_art = f.name
    get_art(logo, artlib=None, file=_new_art, verbose=False)
    # Prefer bat on mac if available, fallback to cat
    pager = "bat" if (platform.system() == "Darwin" and any((Path(p).joinpath("bat").exists() for p in os.environ.get("PATH", "").split(os.pathsep)))) else "cat"
    command = f"{pager} {_new_art} | lolcat"
    os.system(command)


if __name__ == '__main__':
    pass
