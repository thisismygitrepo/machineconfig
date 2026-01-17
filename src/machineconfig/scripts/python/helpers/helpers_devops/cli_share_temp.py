
import json
import sys
from pathlib import Path
from typing import Annotated

import requests
import typer


TEMP_BASE_URL: str = "https://temp.sh"
UPLOAD_ENDPOINT: str = f"{TEMP_BASE_URL}/upload"


def _extract_url(response: requests.Response) -> str:
	content_type = response.headers.get("content-type", "")
	text = response.text.strip()
	if "application/json" in content_type:
		try:
			data = response.json()
		except (json.JSONDecodeError, ValueError):
			data = None
		if isinstance(data, dict):
			url_value = data.get("url") or data.get("link") or data.get("download")
			if isinstance(url_value, str) and url_value.strip() != "":
				return url_value.strip()
	for token in text.split():
		if token.startswith("https://") or token.startswith("http://"):
			return token
	return text


def _upload_file_handle(file_name: str, file_handle: object, content_type: str | None) -> str:
	files: dict[str, tuple[str, object, str] | tuple[str, object]]
	if content_type is None:
		files = {"file": (file_name, file_handle)}
	else:
		files = {"file": (file_name, file_handle, content_type)}
	response = requests.post(UPLOAD_ENDPOINT, files=files)  # type: ignore[reportArgumentType]
	response.raise_for_status()
	return _extract_url(response=response)


def upload_file(
	file_path: Annotated[Path, typer.Argument(..., exists=True, dir_okay=False, readable=True)],
) -> None:
	try:
		with file_path.open("rb") as file_handle:
			url = _upload_file_handle(file_name=file_path.name, file_handle=file_handle, content_type=None)
	except requests.RequestException as exc:
		typer.echo(f"Upload failed: {exc}")
		raise typer.Exit(1)
	typer.echo(url)


def upload_text(
	text: Annotated[str, typer.Argument(...)],
) -> None:
	text_value = text
	if text == "-":
		text_value = sys.stdin.read()
	try:
		payload = text_value.encode("utf-8")
		url = _upload_file_handle(file_name="text.txt", file_handle=payload, content_type="text/plain; charset=utf-8")
	except requests.RequestException as exc:
		typer.echo(f"Upload failed: {exc}")
		raise typer.Exit(1)
	typer.echo(url)

