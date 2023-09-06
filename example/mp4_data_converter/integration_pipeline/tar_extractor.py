import logging
import shutil
from pathlib import Path
from typing import Any, Dict

from example.mp4_data_converter.utils.tar_executor import TarExecutor
from src.integration_pipeline.base.pipeline_element import PipelineElement
from src.integration_pipeline.base.pipeline_element_exceptions import PipelineElementError, Severity


class TarExtractor(PipelineElement):
    def __init__(self, settings):
        super().__init__(settings=settings)

    def run(self, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> Dict[str, Any]:
        frames_directory = Path(inputs["anonymized_tar_files_directory"])
        tars_anonymized = sorted([f for f in frames_directory.glob("*.tar")])

        if len(tars_anonymized) == 0:
            message = f"There are no tar files in  the {frames_directory}. Please check the directory."
            raise PipelineElementError(public_message=message, severity=Severity.major, log_message=message)

        output_directory = Path(outputs["directory_anonymized_frames"])
        output_directory.mkdir(parents=True, exist_ok=True)

        tar_executor = TarExecutor(image_extenstion="png")

        logging.info(f"started to extract frames using archives from {frames_directory} into the {output_directory}")
        try:
            tar_executor.extract_files(
                archives_paths=tars_anonymized,
                out_directory_path=output_directory,
            )
        except Exception as e:
            message = f"Failed to extract frames from the archive(s): {e}"
            raise PipelineElementError(public_message=message, severity=Severity.major, log_message=message)

        logging.info("finished extracting frames")

        return {"directory_anonymized_frames": output_directory}

    def cleanup(self, outputs: Dict[str, Any]) -> None:
        output_directory = Path(outputs["directory_anonymized_frames"])

        if output_directory.is_dir():
            logging.debug(f"cleaning up {output_directory}")
            shutil.rmtree(path=output_directory, ignore_errors=True)
