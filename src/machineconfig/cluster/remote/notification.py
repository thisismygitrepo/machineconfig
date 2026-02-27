from machineconfig.cluster.remote.models import EmailParams


NOTIFICATION_TEMPLATE = '''
try:
    from machineconfig.utils.notifications import Email
    msg = f"""
Hi `{addressee}`, I'm `{speaker}`.

Job completed for: `{executed_obj}`

Error: `{{params.error_message}}`

Pull results:
`ftprx {ssh_conn_str} {{res_folder}} -r`
"""
    Email.send_and_close(config_name="{email_config_name}", to="{to_email}", subject=f"Job completed: {{manager.job_id}}", body=msg)
    print("Notification email sent to `{to_email}`.")
except Exception as _notification_err:
    print(f"Failed to send notification email: {{_notification_err}}")
'''


def render_notification_block(email_params: EmailParams) -> str:
    return NOTIFICATION_TEMPLATE.format(
        addressee=email_params.addressee,
        speaker=email_params.speaker,
        executed_obj=email_params.executed_obj,
        ssh_conn_str=email_params.ssh_conn_str,
        email_config_name=email_params.email_config_name,
        to_email=email_params.to_email,
    )
