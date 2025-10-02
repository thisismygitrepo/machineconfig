

from pathlib import Path
from zipfile import ZipFile, BadZipFile
from typing import Union


def decompress_and_remove_zip(zip_path: Union[str, Path]) -> None:
    """
    Decompress a ZIP file and remove it after extraction.

    Args:
        zip_path (Union[str, Path]): Path to the ZIP file.

    Raises:
        FileNotFoundError: If the zip file does not exist.
        BadZipFile: If the file is not a valid ZIP archive.
        PermissionError: If the file cannot be deleted due to permission issues.
        Exception: For other unexpected errors.
    """
    zip_path = Path(zip_path)

    if not zip_path.exists():
        raise FileNotFoundError(f"The file '{zip_path}' does not exist.")
    
    if not zip_path.is_file():
        raise FileNotFoundError(f"The path '{zip_path}' is not a file.")

    extract_dir = zip_path.parent

    try:
        with ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    except BadZipFile as e:
        raise BadZipFile(f"The file '{zip_path}' is not a valid zip archive.") from e
    except Exception as e:
        raise Exception(f"Failed to extract '{zip_path}': {e}") from e

    try:
        zip_path.unlink()
    except PermissionError as e:
        raise PermissionError(f"Permission denied when deleting '{zip_path}'.") from e
    except Exception as e:
        raise Exception(f"Failed to delete '{zip_path}': {e}") from e

