
# install https://visualstudio.microsoft.com/visual-cpp-build-tools/
# include
# winget install Microsoft.VisualStudio.2022.BuildTools
# winget install Microsoft.VC++2015-2022Redist-x86


. "$env:USERPROFILE\code\machineconfig\.venv\Scripts\Activate.ps1"
Set-Location C:
python -m pip install --global-option=build_ext --global-option="-IC:\Program Files\Graphviz\include" --global-option="-LC:\Program Files\Graphviz\lib" pygraphviz
# not including the options as above (from https://pygraphviz.github.io/documentation/stable/install.html)
# would result in an error like this: pygraphviz/graphviz_wrap.c(2711): fatal error C1083: Cannot open include file: 'graphviz/cgraph.h': No such file or directory


