import logging
from pathlib import Path
from typing import Any, Dict

from example.mp4_data_converter.utils.ffmpeg_executor import FFMPEGExecutor
from src.integration_pipeline.base.pipeline_element import PipelineElement
from src.integration_pipeline.base.pipeline_element_exceptions import PipelineElementError, Severity


class DataWriter(PipelineElement):
    def __init__(self, settings):
        super().__init__(settings=settings)

    def run(self, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> Dict[str, Any]:
        input_directory = Path(inputs["directory_anonymized_frames"])
        if len(list(input_directory.glob("*.png"))) == 0:
            message = (
                f"The anonymized frames directory {input_directory} is invalid. "
                f"Please check if it contains PNG files"
            )
            raise PipelineElementError(public_message=message, severity=Severity.major, log_message=message)

        output_directory = Path(outputs["directory_anonymized_data_video"])
        output_directory.mkdir(parents=True, exist_ok=True)

        ffmpeg_executor = FFMPEGExecutor(file_name_format=self._settings["frame_file_name_format"])

        logging.info(f"started to create video using frames from the {input_directory}")
        try:
            ffmpeg_executor.create_video(
                frames_directory=input_directory,
                output_directory=output_directory,
                video_metadata=inputs["video_metadata"],
            )
        except ChildProcessError as e:
            message = f"Failed to create video: {e}"
            raise PipelineElementError(public_message=message, severity=Severity.major, log_message=message)

        logging.info(f"finished creating video and saved it into the {output_directory}")

        return {"directory_anonymized_data_video": output_directory}

    def cleanup(self, outputs: Dict[str, Any]) -> None:
        pass
