import logging
import shutil
from pathlib import Path
from typing import Any, Dict

from example.mp4_data_converter.utils.ffmpeg_executor import FFMPEGExecutor
from src.integration_pipeline.base.pipeline_element import PipelineElement
from src.integration_pipeline.base.pipeline_element_exceptions import PipelineElementError, Severity


class DataReader(PipelineElement):
    def __init__(self, settings):
        super().__init__(settings=settings)

    def run(self, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> Dict[str, Any]:
        video_file = list(Path(inputs["directory_data_video"]).glob("*.mp4"))[0]
        ffmpeg_executor = FFMPEGExecutor(file_name_format=self._settings["frame_file_name_format"])
        output_directory = Path(outputs["directory_extracted_frames"])
        output_directory.mkdir(parents=True, exist_ok=True)

        logging.info(f"started to extract frames from {video_file} into the {output_directory}")
        try:
            video_metadata = ffmpeg_executor.extract_frames(
                file_path=video_file,
                output_directory=output_directory,
            )
        except ChildProcessError as e:
            message = f"Failed to extract frames from the video: {e}"
            raise PipelineElementError(public_message=message, severity=Severity.major, log_message=message)

        logging.info("finished extracting frames")

        return {"directory_extracted_frames": output_directory, "video_metadata": video_metadata}

    def cleanup(self, outputs: Dict[str, Any]) -> None:
        output_directory = Path(outputs["directory_extracted_frames"])

        if output_directory.is_dir():
            logging.debug(f"cleaning up {output_directory}")
            shutil.rmtree(path=output_directory, ignore_errors=True)
