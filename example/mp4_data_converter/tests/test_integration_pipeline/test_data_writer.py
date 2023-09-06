from pathlib import Path
from typing import Any, Dict

import pytest
from pytest_mock import MockFixture

from example.mp4_data_converter.integration_pipeline.data_writer import DataWriter
from src.integration_pipeline.base.pipeline_element_exceptions import PipelineElementError


class TestDataWriter:
    file_name_format = "%08d"

    @pytest.fixture
    def video_metadata(self) -> Dict[str, Any]:
        return {
            "audio_codec": None,
            "avg_frame_rate": "30/1",
            "bit_rate": 2760945,
            "codec_name": "h264",
            "display_aspect_ratio": "16:9",
            "duration": "3.333333",
            "height": 720,
            "name": "test_video.mp4",
            "pix_fmt": "yuv420p",
            "width": 1280,
        }

    def test_run(self, mocker: MockFixture, tmp_path: Path, video_metadata: Dict[str, Any]) -> None:
        mocker.patch(
            target="example.mp4_data_converter.integration_pipeline.data_writer.FFMPEGExecutor.create_video",
            return_value={},
        )
        mocker.patch(
            target="example.mp4_data_converter.integration_pipeline.data_writer.Path.glob", return_value=["frame.png"]
        )

        data_writer = DataWriter(settings={"frame_file_name_format": self.file_name_format})

        result = data_writer.run(
            inputs={"directory_anonymized_frames": tmp_path, "video_metadata": video_metadata},
            outputs={"directory_anonymized_data_video": tmp_path},
        )

        assert result == {"directory_anonymized_data_video": tmp_path}

    def test_run_raises(self, mocker: MockFixture, tmp_path: Path, video_metadata: Dict[str, Any]) -> None:
        mock_exception = ChildProcessError("test")
        mocker.patch(
            target="example.mp4_data_converter.integration_pipeline.data_writer.FFMPEGExecutor.create_video",
            side_effect=mock_exception,
        )
        mocker.patch(
            target="example.mp4_data_converter.integration_pipeline.data_writer.Path.glob", return_value=["frame.png"]
        )

        data_writer = DataWriter(settings={"frame_file_name_format": self.file_name_format})

        with pytest.raises(PipelineElementError):
            data_writer.run(
                inputs={"directory_anonymized_frames": tmp_path, "video_metadata": video_metadata},
                outputs={"directory_anonymized_data_video": tmp_path},
            )

    def test_run_invalid_directory_raises(
        self, mocker: MockFixture, tmp_path: Path, video_metadata: Dict[str, Any]
    ) -> None:
        mocker.patch(
            target="example.mp4_data_converter.integration_pipeline.data_writer.FFMPEGExecutor.create_video",
            return_value={},
        )
        mocker.patch(target="example.mp4_data_converter.integration_pipeline.data_writer.Path.glob", return_value=[])

        data_writer = DataWriter(settings={"frame_file_name_format": self.file_name_format})

        with pytest.raises(PipelineElementError):
            data_writer.run(
                inputs={"directory_anonymized_frames": tmp_path, "video_metadata": video_metadata},
                outputs={"directory_anonymized_data_video": tmp_path},
            )
