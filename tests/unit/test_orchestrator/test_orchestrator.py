from pathlib import Path
from typing import Any, Callable, Dict, List

import pytest
from pytest_mock import MockerFixture

from src.integration_pipeline.base.pipeline_element_exceptions import PipelineElementError, Severity
from src.orchestrator.orchestrator import Orchestrator


class TestOrchestrator:
    @pytest.fixture
    def mock_yaml_parser(self, mocker: MockerFixture) -> Callable:
        def _yaml_parser(pipeline_definition: List[Dict]) -> mocker.MagicMock:
            mock_yaml_parser = mocker.MagicMock
            mock_yaml_parser.get_pipeline_definition = mocker.Mock(return_value=pipeline_definition)

            return mock_yaml_parser

        return _yaml_parser

    @pytest.fixture
    def mock_pipeline_modules(self, mocker: MockerFixture) -> Callable:
        def _mock_pipeline_modules(
            pipeline_elements_modules: Dict[str, str], pipeline_element_class: Any, exception: Exception = None
        ) -> mocker.MagicMock:
            mock_pipeline_modules = mocker.MagicMock

            mock_pipeline_modules.get_all_pipeline_element_modules = mocker.Mock(
                return_value=pipeline_elements_modules, side_effect=exception
            )

            mock_pipeline_modules.get_pipeline_element_class = mocker.Mock(
                return_value=pipeline_element_class, side_effect=exception
            )

            return mock_pipeline_modules

        return _mock_pipeline_modules

    @pytest.fixture
    def validator(self, mocker: MockerFixture) -> Callable:
        def _validator(run_output: Dict[str, Any], exception: Exception = None) -> Any:
            class Validator:
                def __init__(self, settings):
                    self._settings = settings

            Validator.run = mocker.Mock(return_value=run_output, side_effect=exception)

            return Validator

        return _validator

    def test_initialize_pipeline_elements(
        self, mock_yaml_parser: Callable, mock_pipeline_modules: Callable, validator: Callable
    ) -> None:
        yaml_parser = mock_yaml_parser(
            pipeline_definition=[{"name": "Validator", "inputs": {"directory_data_video": "./data/input/"}}]
        )

        validator_class = validator(run_output={})

        pipeline_modules = mock_pipeline_modules(
            pipeline_elements_modules={"validator": "validator_path"}, pipeline_element_class=validator_class
        )

        orchestrator = Orchestrator(yaml_parser=yaml_parser, pipeline_modules=pipeline_modules)

        orchestrator.initialize_pipeline_elements(pipeline_definition_file=Path())

        pipeline_elements = orchestrator._pipeline_elements

        yaml_parser.get_pipeline_definition.assert_called_once()
        pipeline_modules.get_all_pipeline_element_modules.assert_called_once()
        pipeline_modules.get_pipeline_element_class.assert_called_once()

        assert len(pipeline_elements) == 1

        pipeline_element_object = pipeline_elements[0]["object"]
        assert isinstance(pipeline_element_object, validator_class)
        assert pipeline_element_object._settings is None

    @pytest.mark.parametrize(
        "exception",
        [ModuleNotFoundError, KeyError, ImportError],
    )
    def test_initialize_pipeline_elements_raises_system_exit(
        self, mock_yaml_parser: Callable, mock_pipeline_modules: Callable, exception: Exception
    ) -> None:
        yaml_parser = mock_yaml_parser(pipeline_definition=[])

        pipeline_modules = mock_pipeline_modules(
            pipeline_elements_modules={}, pipeline_element_class=None, exception=exception
        )

        orchestrator = Orchestrator(yaml_parser=yaml_parser, pipeline_modules=pipeline_modules)

        with pytest.raises(SystemExit):
            orchestrator.initialize_pipeline_elements(pipeline_definition_file=Path())

        yaml_parser.get_pipeline_definition.assert_called_once()
        pipeline_modules.get_all_pipeline_element_modules.assert_called_once()

    @pytest.mark.parametrize(
        "pipeline_definition, run_output",
        [
            [
                {
                    "name": "Validator",
                    "inputs": {"directory_data_video": "./data/input/"},
                    "outputs": {"key": "value"},
                },
                {"key": "value"},
            ],
            [{"name": "Validator", "inputs": {"directory_data_video": "./data/input/"}}, {}],
        ],
    )
    def test_run_pipeline_elements(
        self,
        mocker: MockerFixture,
        mock_yaml_parser: Callable,
        mock_pipeline_modules: Callable,
        validator: Callable,
        pipeline_definition: Dict[str, Any],
        run_output: Dict[str, Any],
    ) -> None:
        yaml_parser = mock_yaml_parser(pipeline_definition=[pipeline_definition])

        validator_class = validator(run_output=run_output)

        pipeline_modules = mock_pipeline_modules(
            pipeline_elements_modules={"validator": "validator_path"}, pipeline_element_class=validator_class
        )

        orchestrator = Orchestrator(yaml_parser=yaml_parser, pipeline_modules=pipeline_modules)
        orchestrator.initialize_pipeline_elements(pipeline_definition_file=Path())

        orchestrator.run_pipeline_element()

        validator_class.run.assert_called_once()

        assert orchestrator._outputs == run_output

    @pytest.mark.parametrize(
        "pipeline_definition, run_output",
        [
            [{"name": "Validator", "inputs": {"directory_data_video": "./data/input/"}, "outputs": {}}, {}],
            [{"name": "Validator", "inputs": {"directory_data_video": "./data/input/"}}, {"key": "value"}],
        ],
    )
    def test_run_pipeline_elements_raises_value_error(
        self,
        mock_yaml_parser: Callable,
        mock_pipeline_modules: Callable,
        validator: Callable,
        pipeline_definition: Dict[str, Any],
        run_output: Dict[str, Any],
    ) -> None:
        yaml_parser = mock_yaml_parser(pipeline_definition=[pipeline_definition])

        validator_class = validator(run_output=run_output)

        pipeline_modules = mock_pipeline_modules(
            pipeline_elements_modules={"validator": "validator_path"}, pipeline_element_class=validator_class
        )

        orchestrator = Orchestrator(yaml_parser=yaml_parser, pipeline_modules=pipeline_modules)
        orchestrator.initialize_pipeline_elements(pipeline_definition_file=Path())

        with pytest.raises(ValueError):
            orchestrator.run_pipeline_element()

        validator_class.run.assert_called_once()

    @pytest.mark.parametrize(
        "exception",
        [
            PipelineElementError(public_message="", severity=Severity.minor, log_message=""),
            PipelineElementError(public_message="", severity=Severity.major, log_message=""),
        ],
    )
    def test_run_pipeline_elements_handles_pipeline_element_exceptions(
        self,
        mock_yaml_parser: Callable,
        mock_pipeline_modules: Callable,
        validator: Callable,
        exception: Exception,
    ) -> None:
        yaml_parser = mock_yaml_parser(
            pipeline_definition=[
                {"name": "Validator", "inputs": {"directory_data_video": "./data/input/"}, "outputs": {}}
            ]
        )

        validator_class = validator(run_output={}, exception=exception)

        pipeline_modules = mock_pipeline_modules(
            pipeline_elements_modules={"validator": "validator_path"}, pipeline_element_class=validator_class
        )

        orchestrator = Orchestrator(yaml_parser=yaml_parser, pipeline_modules=pipeline_modules)
        orchestrator.initialize_pipeline_elements(pipeline_definition_file=Path())

        if exception.severity == Severity.minor:
            orchestrator.run_pipeline_element()

            assert orchestrator._outputs == {}

        elif exception.severity == Severity.major:
            with pytest.raises(SystemExit):
                orchestrator.run_pipeline_element()
