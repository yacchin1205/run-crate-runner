import argparse
import datetime
import json
import logging
import os
import shutil
import tempfile
from uuid import uuid4

from . import crate
from .runner import run_notebook

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    prog="run-crate",
    description="Run a Jupyter notebook and save the output as a Run-Crate."
)
parser.add_argument(
    "notebook_or_crate",
    help="The notebook to run."
)
parser.add_argument(
    "output",
    help="The output file."
)
parser.add_argument(
    "--log-level",
    default="WARNING",
    help="The log level to use."
)

def main():
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level)

    work_dir = tempfile.mkdtemp()
    try:
        default_crate = '~/run-crate-metadata.json'
        if 'RUN_CRATE_METADATA' in os.environ:
            default_crate = os.environ['RUN_CRATE_METADATA']
        default_crate = os.path.expanduser(default_crate)
        id = os.environ['RUN_CRATE_ID'] if 'RUN_CRATE_ID' in os.environ else uuid4()
        start_time = datetime.datetime.now()
        output_notebook = os.path.join(work_dir, f"output-{id}.ipynb")
        input_as_crate = os.path.splitext(args.notebook_or_crate)[1].lower() != ".ipynb"
        notebook = crate.extract_notebook(args.notebook_or_crate) if input_as_crate else args.notebook_or_crate
        notebook = os.path.expanduser(notebook)
        logger.info(f"Running notebook {notebook} and saving output to {output_notebook}")
        (exit_code, stdout, stderr) = run_notebook(notebook, output_notebook)
        logger.info(f"Result: {exit_code}, {stdout}, {stderr}")
        crate_content = crate.create(
            id,
            os.path.expanduser(args.notebook_or_crate) if input_as_crate else default_crate,
            notebook,
            output_notebook,
            start_time,
            exit_code,
            stdout,
            stderr,
        )
        if args.output == '-':
            print(json.dumps(crate_content, indent=2, sort_keys=True))
            return
        with open(args.output, 'w') as f:
            json.dump(crate_content, f, indent=2, sort_keys=True)
    finally:
        shutil.rmtree(work_dir)
