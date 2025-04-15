
"""
Notify User Upon Completion
"""

from crocodile.comms.notification import Email
from crocodile.core import Struct as S
from crocodile.file_management import P
from machineconfig.cluster.file_manager import FileManager
from machineconfig.cluster.loader_runner import EmailParams


error_message = ''
exec_times = S()
res_folder = P()

email_params = EmailParams.from_empty()
manager = FileManager.from_pickle(email_params.file_manager_path)

print(f'SENDING notification email using `{email_params.email_config_name}` email configuration ...')

sep = "\n" * 2  # SyntaxError: f-string expression part cannot include a backslash, keep it here outside fstring.
msg = f'''

Hi `{email_params.addressee}`, I'm `{email_params.speaker}`, this is a notification that I have completed running the script you sent to me.

``` {email_params.executed_obj} ```


#### Error Message:
`{error_message}`
#### Execution Times
{exec_times.print(as_config=True, return_str=True)}
#### Executed Shell Script:
`{manager.shell_script_path}`
#### Executed Python Script:
`{manager.py_script_path}`

#### Pull results using this script:
`ftprx {email_params.ssh_conn_str} {res_folder.collapseuser().as_posix()} -r`
Or, using croshell,

```python

ssh = SSH(r'{email_params.ssh_conn_str}')
ssh.copy_to_here(r'{res_folder.collapseuser().as_posix()}', r=False, zip_first=False)

```

#### Results folder contents:
```

{res_folder.search().print(return_str=True, sep=sep)}

```

'''

try:
    Email.send_and_close(config_name=email_params.email_config_name, to=email_params.to_email,
                         subject=f"Execution Completion Notification, job_id = {manager.job_id}", body=msg)
    print(f'FINISHED sending notification email to `{email_params.to_email}`')
except Exception as e: print(f"Error sending email: {e}")
