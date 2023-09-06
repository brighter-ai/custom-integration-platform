import logging
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

from src.integration_pipeline.base.pipeline_element import PipelineElement
from src.integration_pipeline.base.pipeline_element_exceptions import PipelineElementError, Severity


class Validator(PipelineElement):
    def __init__(self, settings):
        super().__init__(settings=settings)

    def run(self, inputs: Dict[str, Any], outputs: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        input_directory = Path(inputs["directory_data_video"]).absolute()

        logging.info(f"validating input directory {input_directory}")
        if not self._is_input_directory_valid(input_directory=input_directory):
            raise PipelineElementError(
                public_message=(
                    f"The input directory {input_directory} is invalid. "
                    f"Please check if the directory exists and has a MP4 file"
                ),
                severity=Severity.major,
                log_message=f"the input directory {input_directory} either does not exist or "
                f"does not contain any MP4 files",
            )

        logging.info(f"validating redact on {inputs['redact_url']}")
        if not self._is_redact_working(redact_url=inputs["redact_url"]):
            raise PipelineElementError(
                public_message=(
                    "Redact is not operational. Please check if the redact container is running and functional"
                ),
                severity=Severity.major,
                log_message="redact status is not 'operational'",
            )

        return {}

    @staticmethod
    def _is_input_directory_valid(input_directory: Path) -> bool:
        return input_directory.is_dir() and len(list(input_directory.glob("*.mp4"))) > 0

    @staticmethod
    def _is_redact_working(redact_url: str) -> bool:
        redact_health_url = f"{redact_url}/v4/health"
        try:
            response = httpx.get(redact_health_url)
            logging.debug(f"response: {response.text}")
            return response.json().get("status") == "operational"
        except httpx.HTTPError as e:
            raise PipelineElementError(
                public_message="An error occurred while checking redact health status",
                severity=Severity.major,
                log_message=f"redact health check {redact_health_url} failed with {e}",
            )

    def cleanup(self, outputs: Optional[Dict[str, Any]]) -> None:
        pass
