

import crocodile.toolbox as tb

# one can either install rufus: https://rufus.ie/en/
# however, to create bootable media with multiple OSs to choose from:

tb.P(r'https://github.com/ventoy/Ventoy/archive/refs/tags/v1.0.78.zip').download().unzip().find()()
