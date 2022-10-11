
import crocodile.toolbox as tb
import machineconfig.jobs.python_windows_installers as inst
import machineconfig.jobs.python_generic_installers as gens

tb.P(inst.__file__).parent.search("*.py").apply(tb.Read.py)
tb.P(gens.__file__).parent.search("*.py").apply(tb.Read.py)
