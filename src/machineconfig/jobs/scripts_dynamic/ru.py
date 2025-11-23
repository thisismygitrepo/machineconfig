"""
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "pillow-heif",
#  "pillow",
# ]
# ///

"""


from PIL import Image
import pillow_heif
import os
from pathlib import Path

def convert_heic_to_png(input_path, output_path):
    """Convert a single HEIC file to PNG."""
    heif_file = pillow_heif.read_heif(input_path)
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw"
    )
    image.save(output_path, format="PNG")
    print(f"Converted {input_path} -> {output_path}")

# Current directory
current_dir = Path(".")

# Find all HEIC files in current directory
heic_files = list(current_dir.glob("*.heic"))

if not heic_files:
    print("No HEIC files found in current directory.")
else:
    for heic_file in heic_files:
        output_file = heic_file.with_suffix(".png")
        convert_heic_to_png(heic_file, output_file)

