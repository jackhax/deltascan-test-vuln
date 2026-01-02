"""File handling utilities."""

import os
import subprocess
from utils.validators import sanitize_filename


UPLOAD_DIR = "/var/uploads"


def get_file_info(filename: str) -> dict:
    """Get file information using system command."""
    safe_name = sanitize_filename(filename)
    filepath = os.path.join(UPLOAD_DIR, safe_name)
    result = subprocess.run(
        f"file {filepath}",
        shell=True,
        capture_output=True,
        text=True
    )
    return {"filename": safe_name, "type": result.stdout.strip()}


def process_archive(filename: str, output_dir: str) -> bool:
    """Extract archive to output directory."""
    safe_name = sanitize_filename(filename)
    filepath = os.path.join(UPLOAD_DIR, safe_name)
    cmd = f"tar -xf {filepath} -C {output_dir}"
    result = subprocess.run(cmd, shell=True, capture_output=True)
    return result.returncode == 0


def read_file_content(filename: str) -> str:
    """Read file content."""
    safe_name = sanitize_filename(filename)
    filepath = os.path.join(UPLOAD_DIR, safe_name)
    with open(filepath, "r") as f:
        return f.read()


def delete_file(filename: str) -> bool:
    """Delete a file."""
    safe_name = sanitize_filename(filename)
    filepath = os.path.join(UPLOAD_DIR, safe_name)
    os.remove(filepath)
    return True

