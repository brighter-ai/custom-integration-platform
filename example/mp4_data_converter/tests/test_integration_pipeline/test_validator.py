from pathlib import Path
from typing import Any, Callable, Dict, List

import httpx
import pytest
from httpx import HTTPError
from pytest_mock import MockerFixture

from example.mp4_data_converter.integration_pipeline.validator import Validator
from src.integration_pipeline.base.pipeline_element_exceptions import PipelineElementError


class TestValidator:
    @pytest.fixture
    def mock_response(self, mocker: MockerFixture) -> Callable:
        def _mock_response(return_value: Any, error: bool = False) -> mocker.Mock:
            mock_response = mocker.Mock()
            mock_response.json.return_value = return_value
            mock_response.text = str(return_value)

            if error:
                mock_response.side_effect = HTTPError("Test error")

            return mock_response

        return _mock_response

    @pytest.mark.parametrize(
        "is_dir,glob,result",
        [[True, [Path("test.mp4")], True], [False, [Path("test.mp4")], False], [True, [], False]],
    )
    def test_is_input_directory_valid(
        self, mocker: MockerFixture, is_dir: bool, glob: List[Path], result: bool
    ) -> None:
        mocker.patch.object(target=Path, attribute="is_dir", return_value=is_dir)
        mocker.patch.object(target=Path, attribute="glob", return_value=glob)

        temp = Path("temp")

        validator = Validator(settings={})

        assert validator._is_input_directory_valid(temp) == result

    @pytest.mark.parametrize(
        "response_body,result",
        [
            [{"status": "operational"}, True],
            [{"status": "unknown"}, False],
        ],
    )
    def test_redact_is_working(
        self, mocker: MockerFixture, mock_response: Callable, response_body: Dict[str, Any], result: bool
    ) -> None:
        response = mock_response(return_value=response_body)
        mocker.patch.object(target=httpx, attribute="get", return_value=response)

        validator = Validator(settings={})

        assert validator._is_redact_working(redact_url="test") == result

    def test_is_redact_working_raising(self, mocker: MockerFixture, mock_response: Callable) -> None:
        mocker.patch.object(target=httpx, attribute="get", side_effect=HTTPError("Test error"))

        validator = Validator(settings={})

        with pytest.raises(PipelineElementError):
            validator._is_redact_working(redact_url="test")

    def test_run(self, mocker: MockerFixture, mock_response: Callable) -> None:
        mocker.patch.object(target=Path, attribute="is_dir", return_value=True)
        mocker.patch.object(target=Path, attribute="glob", return_value=[Path("test.mp4")])
        response = mock_response(return_value={"status": "operational"})
        mocker.patch.object(target=httpx, attribute="get", return_value=response)

        temp = Path("temp")

        validator = Validator(settings={})

        assert validator.run({"directory_data_video": temp, "redact_url": "test"}, outputs={}) == {}

    @pytest.mark.parametrize(
        "is_dir,glob,response_body",
        [
            [False, [Path("test.mp4")], {"status": "operational"}],
            [True, [], {"status": "operational"}],
            [True, [Path("test.mp4")], {"status": "unknown"}],
        ],
    )
    def test_run_raises(
        self,
        mocker: MockerFixture,
        is_dir: bool,
        glob: List[Path],
        mock_response: Callable,
        response_body: Dict[str, Any],
    ) -> None:
        mocker.patch.object(target=Path, attribute="is_dir", return_value=is_dir)
        mocker.patch.object(target=Path, attribute="glob", return_value=glob)
        response = mock_response(return_value=response_body)
        mocker.patch.object(target=httpx, attribute="get", return_value=response)

        temp = Path("temp")

        validator = Validator(settings={})

        with pytest.raises(PipelineElementError):
            validator.run(inputs={"directory_data_video": temp, "redact_url": "test"}, outputs={})
