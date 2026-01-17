import subprocess


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
	result = subprocess.run(command, capture_output=True, text=True, check=False)
	return result


def run_command_sudo(command: list[str]) -> subprocess.CompletedProcess[str]:
	result = subprocess.run(["sudo", *command], capture_output=True, text=True, check=False)
	return result


def run_powershell(command: str) -> subprocess.CompletedProcess[str]:
	result = subprocess.run(["powershell", "-NoProfile", "-Command", command], capture_output=True, text=True, check=False)
	return result


def ensure_ok(result: subprocess.CompletedProcess[str], context: str) -> str:
	if result.returncode != 0:
		stderr_value = result.stderr.strip()
		stdout_value = result.stdout.strip()
		error_text = stderr_value if stderr_value != "" else stdout_value
		raise RuntimeError(f"{context} failed: {error_text}")
	return result.stdout
