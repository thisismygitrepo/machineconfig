
import sys
import os
from unittest.mock import patch, MagicMock
from machineconfig.scripts.python.helpers.helpers_msearch.msearch_impl import machineconfig_search

def test_stdin():
    # Mock sys.stdin
    with patch('sys.stdin') as mock_stdin:
        mock_stdin.isatty.return_value = False
        mock_stdin.read.return_value = "Hello World"
        
        # Mock exit_then_run_shell_script to avoid exit
        with patch('machineconfig.utils.code.exit_then_run_shell_script') as mock_exit:
            machineconfig_search(path=".", ast=False, symantic=False, extension="", file=False, no_dotfiles=False, rga=False, install_dependencies=False)
            
            # Check if exit_then_run_shell_script was called
            if mock_exit.called:
                args, kwargs = mock_exit.call_args
                script = kwargs.get('script', args[0] if args else "")
                print("Script content:")
                print(script)
                
                if "rm " in script and "msearch_stdin_" in script:
                    print("SUCCESS: Temp file cleanup found in script.")
                else:
                    print("FAILURE: Temp file cleanup NOT found in script.")
            else:
                print("FAILURE: exit_then_run_shell_script was not called.")

if __name__ == "__main__":
    test_stdin()
