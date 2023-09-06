from pathlib import Path

from pydantic import BaseSettings
from strenum import StrEnum

NAME = "name"
SETTINGS = "settings"
INPUTS = "inputs"
OUTPUTS = "outputs"
OBJECT = "object"


class LogLevel(StrEnum):
    NOTSET: str = "NOTSET"
    DEBUG: str = "DEBUG"
    INFO: str = "INFO"
    WARNING: str = "WARNING"
    ERROR: str = "ERROR"
    CRITICAL: str = "CRITICAL"


class Settings(BaseSettings):
    log_level: LogLevel = LogLevel.INFO
    logs_directory: Path = Path.cwd() / "logs"

    redaction_retry: int = 2
