import logging
import logging.handlers
import pathlib
import sys
from typing import (
    Literal
)
from discord.utils import _ColourFormatter, stream_supports_colour

type Level = Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

default_formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', '%Y-%m-%d %H:%M:%S', style='{')


def setup_logging(level: Level, filepath: pathlib.Path, stderr: bool) -> None:
    root_logger = logging.getLogger()

    if stderr:
        strerr_handler = logging.StreamHandler(sys.stderr)
        if stream_supports_colour(sys.stderr):
            strerr_handler.setFormatter(_ColourFormatter())
        else:
            strerr_handler.setFormatter(default_formatter)
        root_logger.addHandler(strerr_handler)

    try:
        file_handler = logging.handlers.RotatingFileHandler(
            filepath,
            maxBytes=2**18,
            backupCount=3,
            encoding='utf-8',
        )
        file_handler.setFormatter(default_formatter)
        root_logger.addHandler(file_handler)
    except Exception:
        print('failed to set up file-based logging, please check the provided path')
        exit(1)

    root_logger.setLevel(level)

    root_logger.info('Setting up logging complete.')
