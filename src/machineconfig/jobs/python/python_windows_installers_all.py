
import crocodile.toolbox as tb
import machineconfig.jobs.python_windows_installers as inst
from machineconfig.jobs.python_generic_installer.helix import *

tb.P(inst.__file__).parent.search().apply(tb.Read.py)
