import logging
import shutil
from pathlib import Path
from typing import Any, Dict

from redact.v4 import JobArguments, JobState, OutputType, RedactInstance, Region, ServiceType
from retry import retry

from src.integration_pipeline.base.pipeline_element import PipelineElement
from src.integration_pipeline.base.pipeline_element_exceptions import PipelineElementError, Severity
from src.utils.settings import Settings


class Redactor(PipelineElement):
    def __init__(self, settings):
        super().__init__(settings=settings)

    def run(self, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> Dict[str, Any]:
        input_directory = Path(inputs["tar_files_directory"])
        output_directory = Path(outputs["anonymized_tar_files_directory"])
        output_directory.mkdir(parents=True, exist_ok=True)

        if not self._is_tar_archives_directory_valid(tar_files_directory=input_directory):
            raise PipelineElementError(
                public_message=(
                    f"The tar archives directory {input_directory} is invalid. "
                    f"Please check if the directory exists and contains tar files"
                ),
                severity=Severity.major,
                log_message=f"the tar archives directory {input_directory} either does not exist or "
                f"does not contain any tar files",
            )

        for tar_file in input_directory.glob("*.tar"):
            anonymized_tar_file = output_directory / tar_file.name
            logging.info(f"anonymizing the {tar_file}")
            self._redact(
                tar_file=tar_file, redact_url=self._settings["redact_url"], anonymized_tar_file=anonymized_tar_file
            )
            logging.info(f"finished anonymizing the {tar_file}")

        return {"anonymized_tar_files_directory": output_directory}

    @staticmethod
    def _is_tar_archives_directory_valid(tar_files_directory: Path) -> bool:
        return tar_files_directory.is_dir() and len(list(tar_files_directory.glob("*.tar")))

    @retry(PipelineElementError, tries=Settings().redaction_retry)
    def _redact(self, tar_file: Path, redact_url: str, anonymized_tar_file: Path) -> None:
        redact_instance = RedactInstance.create(
            service=ServiceType.blur, out_type=OutputType.archives, redact_url=redact_url
        )

        job_args = JobArguments(
            region=Region.germany,
            face=True,
            license_plate=True,
            face_determination_threshold=self._settings["face_determination_threshold"],
            lp_determination_threshold=self._settings["lp_determination_threshold"],
        )

        with tar_file.open("rb") as f:
            job = redact_instance.start_job(file=f, job_args=job_args)

        job = job.wait_until_finished()
        job_status = job.get_status()
        if job_status.state == JobState.failed:
            message = f"Redacting tarfile {tar_file} failed with error: {job_status.error}"
            raise PipelineElementError(public_message=message, severity=Severity.major, log_message=message)

        job.download_result_to_file(file=anonymized_tar_file)

    def cleanup(self, outputs: Dict[str, Any]) -> None:
        output_directory = Path(outputs["anonymized_tar_files_directory"])

        if output_directory.is_dir():
            logging.debug(f"cleaning up {output_directory}")
            shutil.rmtree(path=output_directory, ignore_errors=True)
