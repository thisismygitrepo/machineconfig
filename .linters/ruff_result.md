F821 Undefined name `PROGRAM_PATH`
  --> src/machineconfig/utils/code.py:85:73
   |
83 |             program = 'orig_path=$(cd -- "." && pwd)\n' + program + '\ncd "$orig_path" || exit'
84 |     if display:
85 |         print_code(code=program, lexer="shell", desc=desc, subtitle=str(PROGRAM_PATH))
   |                                                                         ^^^^^^^^^^^^
86 |     PROGRAM_PATH.parent.mkdir(parents=True, exist_ok=True)
87 |     PROGRAM_PATH.write_text(program, encoding="utf-8")
   |

F821 Undefined name `PROGRAM_PATH`
  --> src/machineconfig/utils/code.py:86:5
   |
84 |     if display:
85 |         print_code(code=program, lexer="shell", desc=desc, subtitle=str(PROGRAM_PATH))
86 |     PROGRAM_PATH.parent.mkdir(parents=True, exist_ok=True)
   |     ^^^^^^^^^^^^
87 |     PROGRAM_PATH.write_text(program, encoding="utf-8")
88 |     if execute:
   |

F821 Undefined name `PROGRAM_PATH`
  --> src/machineconfig/utils/code.py:87:5
   |
85 |         print_code(code=program, lexer="shell", desc=desc, subtitle=str(PROGRAM_PATH))
86 |     PROGRAM_PATH.parent.mkdir(parents=True, exist_ok=True)
87 |     PROGRAM_PATH.write_text(program, encoding="utf-8")
   |     ^^^^^^^^^^^^
88 |     if execute:
89 |         result = subprocess.run(f". {PROGRAM_PATH}", shell=True, capture_output=True, text=True)
   |

F821 Undefined name `PROGRAM_PATH`
  --> src/machineconfig/utils/code.py:89:38
   |
87 |     PROGRAM_PATH.write_text(program, encoding="utf-8")
88 |     if execute:
89 |         result = subprocess.run(f". {PROGRAM_PATH}", shell=True, capture_output=True, text=True)
   |                                      ^^^^^^^^^^^^
90 |         success = result.returncode == 0 and result.stderr == ""
91 |         if not success:
   |

Found 4 errors.
