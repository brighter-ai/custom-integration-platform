from pathlib import Path
from typing import Callable, List
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.orchestrator.pipeline_modules import PipelineModules


class TestPipelineModules:
    @pytest.fixture
    def mock_working_directory(self, mocker: MockerFixture) -> MagicMock:
        return mocker.MagicMock(spec=Path)

    @pytest.fixture
    def mock_modules_path(self, mocker: MockerFixture) -> Callable:
        def _mock_modules_path(mock_modules: List[Path]) -> mocker.MagicMock:
            mock_modules_path = mocker.MagicMock(spec=Path)
            mock_modules_path.rglob = mocker.Mock(return_value=mock_modules)

            return mock_modules_path

        return _mock_modules_path

    def test_get_all_pipeline_element_modules(
        self, mocker: MockerFixture, mock_working_directory: MagicMock, mock_modules_path: Callable
    ) -> None:
        mock_modules_path = mock_modules_path(
            mock_modules=[
                Path("some_module.py"),
                Path("some_package"),
                Path("some_another_module.py"),
                Path("__init__.py"),
                Path("readme.md"),
            ]
        )

        mocker.patch.object(target=Path, attribute="is_file", return_value=True)

        pipeline_modules = PipelineModules(modules_path=mock_modules_path, working_directory=mock_working_directory)
        result = pipeline_modules.get_all_pipeline_element_modules()

        assert result == {"someanothermodule": "some_another_module", "somemodule": "some_module"}

    def test_get_all_pipeline_element_modules_raises(
        self, mocker: MockerFixture, mock_working_directory: MagicMock, mock_modules_path: Callable
    ) -> None:
        mock_modules_path = mock_modules_path(
            mock_modules=[
                Path("some_package"),
                Path("__init__.py"),
                Path("readme.md"),
            ]
        )

        mocker.patch.object(target=Path, attribute="is_file", return_value=True)

        pipeline_modules = PipelineModules(modules_path=mock_modules_path, working_directory=mock_working_directory)

        with pytest.raises(ModuleNotFoundError):
            pipeline_modules.get_all_pipeline_element_modules()

    def test_get_pipeline_element_class(
        self, mocker: MockerFixture, mock_working_directory: MagicMock, mock_modules_path: Callable
    ) -> None:
        mock_modules_path = mock_modules_path(mock_modules=[])
        mock_modules = {"someclass": "some_class_path"}

        class_name = "SomeClass"
        cls = type(class_name, (), {})

        mock_module = mocker.MagicMock()
        mock_module.SomeClass = cls

        mocker.patch(target="src.orchestrator.pipeline_modules.importlib.import_module", return_value=mock_module)

        pipeline_modules = PipelineModules(modules_path=mock_modules_path, working_directory=mock_working_directory)
        result = pipeline_modules.get_pipeline_element_class(modules=mock_modules, class_name=class_name)

        assert result == cls

    def test_get_pipeline_element_class_raises_key_error(
        self, mocker: MockerFixture, mock_working_directory: MagicMock, mock_modules_path: Callable
    ) -> None:
        mock_modules_path = mock_modules_path(mock_modules=[])
        mock_modules = {"someclass": "some_class_path"}

        class_name = "WrongClass"
        cls = type(class_name, (), {})

        mock_module = mocker.MagicMock()
        mock_module.SomeClass = cls

        mocker.patch(target="src.orchestrator.pipeline_modules.importlib.import_module", return_value=mock_module)

        pipeline_modules = PipelineModules(modules_path=mock_modules_path, working_directory=mock_working_directory)
        with pytest.raises(KeyError):
            pipeline_modules.get_pipeline_element_class(modules=mock_modules, class_name=class_name)

    def test_get_pipeline_element_class_raises_import_error(
        self, mocker: MockerFixture, mock_working_directory: MagicMock, mock_modules_path: Callable
    ) -> None:
        mock_modules_path = mock_modules_path(mock_modules=[])
        mock_modules = {"someclass": "some_class_path"}

        class_name = "SomeClass"
        cls = type(class_name, (), {})

        mock_module = mocker.MagicMock()
        mock_module.WrongClass = cls

        mocker.patch(target="src.orchestrator.pipeline_modules.importlib.import_module", return_value=mock_module)

        pipeline_modules = PipelineModules(modules_path=mock_modules_path, working_directory=mock_working_directory)
        with pytest.raises(ImportError):
            pipeline_modules.get_pipeline_element_class(modules=mock_modules, class_name=class_name)
