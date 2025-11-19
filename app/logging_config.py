import logging
import os
import sys
from typing import Optional
from pythonjsonlogger import jsonlogger


def _get_log_level(default: str = "INFO") -> int:
    level_name = os.getenv("LOG_LEVEL", default).upper()
    return getattr(logging, level_name, logging.INFO)


def configure_logging(_: Optional[object] = None) -> logging.Logger:
    """
    Configure a JSON logger that writes to stdout.
    Returns the app logger instance.
    """
    log_level = _get_log_level()

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Ensure no duplicate handlers on reload
    for h in list(root_logger.handlers):
        root_logger.removeHandler(h)

    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Quieten noisy loggers if needed (uncomment as desired)
    # logging.getLogger("werkzeug").setLevel(logging.WARNING)

    app_logger = logging.getLogger("app")
    app_logger.setLevel(log_level)
    return app_logger


