import math
from pathlib import Path
from typing import Any, Dict

import pytest

from example.mp4_data_converter.utils.ffmpeg_executor import FFMPEGExecutor
from example.mp4_data_converter.utils.video_utils import retrieve_video_metadata_from_video_file


class TestFFMPEGExecutor:
    file_name_format = "%08d"

    @pytest.fixture
    def video_metadata(self) -> Dict[str, Any]:
        return {
            "audio_codec": None,
            "avg_frame_rate": "25/1",
            "bit_rate": 1380878,
            "codec_name": "h264",
            "display_aspect_ratio": "16:9",
            "duration": "4.000000",
            "height": 720,
            "name": "test_video.mp4",
            "pix_fmt": "yuv420p",
            "width": 1280,
        }

    def test_extract(self, video_metadata: Dict[str, Any], tmp_path: Path) -> None:
        output_directory = tmp_path / "output"
        output_directory.mkdir(parents=True, exist_ok=True)

        ffmpeg_executor = FFMPEGExecutor(file_name_format=self.file_name_format)

        result = ffmpeg_executor.extract_frames(
            file_path=Path("example/mp4_data_converter/tests/assets/original_video/test_video.mp4"),
            output_directory=output_directory,
        )

        assert len(list(output_directory.glob("*.png"))) == 100

        original_bit_rate = video_metadata.pop("bit_rate")
        result_bit_rate = result.pop("bit_rate")

        assert result == video_metadata

        assert math.isclose(result_bit_rate, original_bit_rate, rel_tol=0.005)

    def test_create_video(self, video_metadata: Dict[str, Any], tmp_path: Path) -> None:
        output_directory = tmp_path / "output"
        output_directory.mkdir(parents=True, exist_ok=True)

        ffmpeg_executor = FFMPEGExecutor(file_name_format=self.file_name_format)

        ffmpeg_executor.create_video(
            frames_directory=Path("example/mp4_data_converter/tests/assets/frames_anonymized"),
            output_directory=output_directory,
            video_metadata=video_metadata,
        )

        video_file = list(output_directory.glob("*.mp4"))[0]
        result = retrieve_video_metadata_from_video_file(video_file_path=video_file)

        assert video_file

        original_bit_rate = video_metadata.pop("bit_rate")
        result_bit_rate = result.pop("bit_rate")

        assert result == video_metadata

        assert math.isclose(result_bit_rate, original_bit_rate, rel_tol=0.4)
