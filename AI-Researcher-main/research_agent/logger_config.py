import logging
from pythonjsonlogger import jsonlogger

import os
from typing import Optional

def setup_logging(job_id: Optional[str] = None):
    """
    Set up structured JSON logging.
    If a job_id is provided, logs will be written to a job-specific file.
    Otherwise, logs will be written to stdout.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create a new handler
    if job_id:
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{job_id}.log")
        handler = logging.FileHandler(log_file)
    else:
        handler = logging.StreamHandler()

    # Create a JSON formatter
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )

    # Set the formatter for the handler
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)
