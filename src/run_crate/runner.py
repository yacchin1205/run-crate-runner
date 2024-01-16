import logging
import subprocess

logger = logging.getLogger(__name__)

def run_notebook(src, dest):
    result = subprocess.run(
        ["papermill", src, dest],
        capture_output=True,
        text=True,
    )
    return (result.returncode, result.stdout, result.stderr)
