/home/alex/code/machineconfig/src/machineconfig/scripts/python/devops.py
  /home/alex/code/machineconfig/src/machineconfig/scripts/python/devops.py:6:46 - error: Import "PathExtended" is not accessed (reportUnusedImport)
  /home/alex/code/machineconfig/src/machineconfig/scripts/python/devops.py:77:5 - error: "PathExtended" is unbound (reportUnboundVariable)
/home/alex/code/machineconfig/src/machineconfig/scripts/python/dotfile.py
  /home/alex/code/machineconfig/src/machineconfig/scripts/python/dotfile.py:35:42 - error: Argument of type "Path | PathExtended" cannot be assigned to parameter "to_this" of type "PathExtended" in function "symlink_func"
    Type "Path | PathExtended" is not assignable to type "PathExtended"
      "Path" is not assignable to "PathExtended" (reportArgumentType)
  /home/alex/code/machineconfig/src/machineconfig/scripts/python/dotfile.py:47:106 - error: Cannot access attribute "collapseuser" for class "Path"
    Attribute "collapseuser" is unknown (reportAttributeAccessIssue)
/home/alex/code/machineconfig/src/machineconfig/utils/path_reduced.py
  /home/alex/code/machineconfig/src/machineconfig/utils/path_reduced.py:533:20 - warning: Import "win32com.shell.shell" could not be resolved from source (reportMissingModuleSource)
4 errors, 1 warning, 0 informations
WARNING: there is a new pyright version available (v1.1.404 -> v1.1.405).
Please install the new version or set PYRIGHT_PYTHON_FORCE_VERSION to `latest`

