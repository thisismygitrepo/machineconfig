/home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/wt_local_manager.py
  /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/wt_local_manager.py:38:13 - error: Argument missing for parameter "layout_config" (reportCallIssue)
  /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/wt_local_manager.py:38:38 - error: No parameter named "tab_config" (reportCallIssue)
  /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/wt_local_manager.py:306:89 - error: Cannot access attribute "tab_config" for class "WTLayoutGenerator"
    Attribute "tab_config" is unknown (reportAttributeAccessIssue)
  /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/wt_local_manager.py:355:29 - error: Cannot assign to attribute "tab_config" for class "WTLayoutGenerator"
    Attribute "tab_config" is unknown (reportAttributeAccessIssue)
  /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/wt_local_manager.py:425:139 - error: Cannot access attribute "tab_config" for class "WTLayoutGenerator"
    Attribute "tab_config" is unknown (reportAttributeAccessIssue)
  /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/wt_local_manager.py:425:173 - error: Cannot access attribute "tab_config" for class "WTLayoutGenerator"
    Attribute "tab_config" is unknown (reportAttributeAccessIssue)
/home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_remote.py
  /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_remote.py:56:69 - error: Argument of type "LayoutConfig" cannot be assigned to parameter "tab_config" of type "Dict[str, Tuple[str, str]]" in function "create_layout_file"
    "LayoutConfig" is not assignable to "Dict[str, Tuple[str, str]]" (reportArgumentType)
  /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_remote.py:60:62 - error: Argument of type "LayoutConfig" cannot be assigned to parameter "tab_config" of type "Dict[str, Tuple[str, str]]" in function "generate_layout_content"
    "LayoutConfig" is not assignable to "Dict[str, Tuple[str, str]]" (reportArgumentType)
  /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_remote.py:65:68 - error: Argument of type "LayoutConfig" cannot be assigned to parameter "tab_config" of type "Dict[str, Tuple[str, str]]" in function "check_command_status"
    "LayoutConfig" is not assignable to "Dict[str, Tuple[str, str]]" (reportArgumentType)
  /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_remote.py:70:63 - error: Argument of type "LayoutConfig" cannot be assigned to parameter "tab_config" of type "Dict[str, Tuple[str, str]]" in function "check_all_commands_status"
    "LayoutConfig" is not assignable to "Dict[str, Tuple[str, str]]" (reportArgumentType)
  /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_remote.py:78:62 - error: Argument of type "LayoutConfig" cannot be assigned to parameter "tab_config" of type "Dict[str, Tuple[str, str]]" in function "get_comprehensive_status"
    "LayoutConfig" is not assignable to "Dict[str, Tuple[str, str]]" (reportArgumentType)
  /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_remote.py:84:50 - error: Argument of type "LayoutConfig" cannot be assigned to parameter "tab_config" of type "Dict[str, Tuple[str, str]]" in function "print_status_report"
    "LayoutConfig" is not assignable to "Dict[str, Tuple[str, str]]" (reportArgumentType)
  /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_remote.py:96:73 - error: Argument of type "LayoutConfig" cannot be assigned to parameter "tab_config" of type "Dict[str, Tuple[str, str]]" in function "force_fresh_process_check"
    "LayoutConfig" is not assignable to "Dict[str, Tuple[str, str]]" (reportArgumentType)
  /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_remote.py:104:75 - error: Argument of type "LayoutConfig" cannot be assigned to parameter "tab_config" of type "Dict[str, Tuple[str, str]]" in function "get_verified_process_status"
    "LayoutConfig" is not assignable to "Dict[str, Tuple[str, str]]" (reportArgumentType)
/home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_remote_manager.py
  /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_remote_manager.py:23:13 - error: Argument missing for parameter "layout_config" (reportCallIssue)
  /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_remote_manager.py:23:39 - error: No parameter named "tab_config" (reportCallIssue)
/home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_utils/example_usage.py
  /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_utils/example_usage.py:29:54 - error: Argument of type "dict[str, tuple[str, str]]" cannot be assigned to parameter "layout_config" of type "LayoutConfig" in function "create_zellij_layout"
    "dict[str, tuple[str, str]]" is not assignable to "LayoutConfig" (reportArgumentType)
  /home/alex/code/machineconfig/src/machineconfig/cluster/sessions_managers/zellij_utils/example_usage.py:33:48 - error: Argument of type "dict[str, tuple[str, str]]" cannot be assigned to parameter "layout_config" of type "LayoutConfig" in function "get_layout_preview"
    "dict[str, tuple[str, str]]" is not assignable to "LayoutConfig" (reportArgumentType)
/home/alex/code/machineconfig/src/machineconfig/scripts/python/fire_agents.py
  /home/alex/code/machineconfig/src/machineconfig/scripts/python/fire_agents.py:231:15 - error: Argument missing for parameter "session_layouts" (reportCallIssue)
  /home/alex/code/machineconfig/src/machineconfig/scripts/python/fire_agents.py:231:34 - error: No parameter named "session2zellij_tabs" (reportCallIssue)
/home/alex/code/machineconfig/src/machineconfig/scripts/python/fire_jobs.py
  /home/alex/code/machineconfig/src/machineconfig/scripts/python/fire_jobs.py:314:9 - error: Argument missing for parameter "layout_config" (reportCallIssue)
  /home/alex/code/machineconfig/src/machineconfig/scripts/python/fire_jobs.py:314:27 - error: No parameter named "tab_config" (reportCallIssue)
/home/alex/code/machineconfig/src/machineconfig/utils/path_reduced.py
  /home/alex/code/machineconfig/src/machineconfig/utils/path_reduced.py:398:20 - warning: Import "win32com.shell.shell" could not be resolved from source (reportMissingModuleSource)
22 errors, 1 warning, 0 informations
