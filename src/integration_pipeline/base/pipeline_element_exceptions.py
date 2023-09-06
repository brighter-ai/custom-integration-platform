from strenum import StrEnum


class Severity(StrEnum):
    major: str = "MAJOR"
    minor: str = "MINOR"


class PipelineElementError(Exception):
    def __init__(
        self,
        public_message: str,
        severity: Severity,
        log_message: str,
    ) -> None:
        self.public_message = public_message
        self.severity = severity
        self.log_message = log_message
