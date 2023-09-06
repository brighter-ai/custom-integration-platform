import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from example.mp4_data_converter.utils.video_utils import retrieve_video_metadata_from_video_file


class FFMPEGExecutor:
    def __init__(self, file_name_format: str):
        self._application = "ffmpeg"

        self._file_name_format = file_name_format

    def extract_frames(self, file_path: Path, output_directory: Path) -> Dict[str, Any]:
        video_metadata = retrieve_video_metadata_from_video_file(video_file_path=file_path)
        command = ["-i", str(file_path.absolute()), str(output_directory.absolute() / f"{self._file_name_format}.png")]

        self._execute(command=command)
        return video_metadata

    def _execute(self, command: List[str]) -> None:
        logging.debug(f"started {self._application}")
        process = subprocess.Popen(
            args=[self._application] + command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        for stdout_line in iter(process.stdout.readline, ""):
            logging.debug(stdout_line)

        process.stdout.close()
        return_code = process.wait(timeout=600)

        logging.debug(f"finished {self._application}")

        if return_code:
            message = f"The {self._application} failed to execute command {' '.join(command)}."
            logging.debug(f"{message} The return code is {return_code}")

            raise ChildProcessError(message)

    def create_video(
        self, frames_directory: Path, output_directory: Path, video_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        command = [
            "-framerate",
            video_metadata["avg_frame_rate"],
            "-i",
            f"{frames_directory}/{self._file_name_format}.png",
            "-c:v",
            video_metadata["codec_name"],
            "-pix_fmt",
            video_metadata["pix_fmt"],
            "-s",
            f"{video_metadata['width']}x{video_metadata['height']}",
            "-aspect",
            video_metadata["display_aspect_ratio"],
            "-b:v",
            str(video_metadata["bit_rate"]),
            str(output_directory / video_metadata["name"]),
            "-y",
        ]

        self._execute(command=command)

        return {}
