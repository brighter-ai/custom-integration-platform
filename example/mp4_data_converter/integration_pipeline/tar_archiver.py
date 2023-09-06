import logging
import shutil
from pathlib import Path
from typing import Any, Dict

from example.mp4_data_converter.utils.tar_executor import TarExecutor
from src.integration_pipeline.base.pipeline_element import PipelineElement
from src.integration_pipeline.base.pipeline_element_exceptions import PipelineElementError, Severity


class TarArchiver(PipelineElement):
    def __init__(self, settings):
        super().__init__(settings=settings)

    def run(self, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> Dict[str, Any]:
        frames_directory = Path(inputs["directory_extracted_frames"])
        frames_paths = sorted([f for f in frames_directory.glob("*.png")])

        if len(frames_paths) == 0:
            message = f"There are no files with extension '.png' to archive in {frames_directory}"
            raise PipelineElementError(public_message=message, severity=Severity.major, log_message=message)

        output_directory = Path(outputs["tar_files_directory"])
        output_directory.mkdir(parents=True, exist_ok=True)

        tar_executor = TarExecutor(image_extenstion="png")

        logging.info(f"started to archive frames from {frames_directory} into the {output_directory}")
        try:
            tar_executor.archive_files(
                images_paths=frames_paths,
                out_directory_path=output_directory,
                num_files=self._settings["number_of_files_in_tar"],
            )
        except Exception as e:
            message = f"Failed to archive frames into the archive(-s): {e}"
            raise PipelineElementError(public_message=message, severity=Severity.major, log_message=message)

        logging.info("finished archiving frames")

        return {"directory_extracted_frames": output_directory}

    def cleanup(self, outputs: Dict[str, Any]) -> None:
        output_directory = Path(outputs["tar_files_directory"])

        if output_directory.is_dir():
            logging.debug(f"cleaning up {output_directory}")
            shutil.rmtree(path=output_directory, ignore_errors=True)
