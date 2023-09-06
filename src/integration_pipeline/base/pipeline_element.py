from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class PipelineElement(ABC):
    def __init__(self, settings: Optional[Dict[str, Any]] = None) -> None:
        self._settings = settings

    @abstractmethod
    def run(self, inputs: Dict[str, Any], outputs: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def cleanup(self, outputs: Optional[Dict[str, Any]]) -> None:
        raise NotImplementedError
