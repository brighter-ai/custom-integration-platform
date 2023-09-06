from pathlib import Path

import pytest
from pytest_mock import MockFixture

from example.mp4_data_converter.integration_pipeline.data_reader import DataReader
from src.integration_pipeline.base.pipeline_element_exceptions import PipelineElementError


class TestDataReader:
    file_name_format = "%08d"

    def test_run(self, mocker: MockFixture, tmp_path: Path) -> None:
        mocker.patch(
            target="example.mp4_data_converter.integration_pipeline.data_reader.FFMPEGExecutor.extract_frames",
            return_value={},
        )
        mocker.patch(
            target="example.mp4_data_converter.integration_pipeline.data_reader.Path.glob", return_value=["video.mp4"]
        )

        data_reader = DataReader(settings={"frame_file_name_format": self.file_name_format})

        result = data_reader.run(
            inputs={"directory_data_video": tmp_path}, outputs={"directory_extracted_frames": tmp_path}
        )

        assert result == {"directory_extracted_frames": tmp_path, "video_metadata": {}}

    def test_run_raises(self, mocker: MockFixture, tmp_path: Path) -> None:
        mock_exception = ChildProcessError("test")
        mocker.patch(
            target="example.mp4_data_converter.integration_pipeline.data_reader.FFMPEGExecutor.extract_frames",
            side_effect=mock_exception,
        )
        mocker.patch(
            target="example.mp4_data_converter.integration_pipeline.data_reader.Path.glob", return_value=["video.mp4"]
        )

        data_reader = DataReader(settings={"frame_file_name_format": self.file_name_format})

        with pytest.raises(PipelineElementError):
            data_reader.run(
                inputs={"directory_data_video": tmp_path}, outputs={"directory_extracted_frames": tmp_path}
            )
