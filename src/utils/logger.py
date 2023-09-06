import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from logfmter import Logfmter

from src.utils.settings import LogLevel, Settings

settings = Settings()


def configure_logging(
    log_level: LogLevel = settings.log_level, logs_directory: Path = settings.logs_directory
) -> None:
    formatter = Logfmter(
        keys=["at", "when", "module"],
        mapping={"at": "levelname", "when": "asctime", "module": "filename"},
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    oldmask = os.umask(0)
    os.makedirs(logs_directory, exist_ok=True, mode=0o777)
    os.umask(oldmask)
    log_file = f"{logs_directory}/{datetime.strftime(datetime.utcnow(), '%Y_%m_%d_%H_%M_%S')}.log"

    file_handler = RotatingFileHandler(filename=log_file, maxBytes=10 * 1024 * 1024, backupCount=5)  # 10 MiB
    file_handler.setFormatter(formatter)

    logging.basicConfig(
        handlers=[stream_handler, file_handler],
        level=logging.getLevelName(log_level),
    )

    logging.debug("logging configured")
