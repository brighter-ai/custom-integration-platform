import logging
import sys
from pathlib import Path
from typing import Any, Dict

from src.orchestrator.exceptions import run_exception
from src.orchestrator.pipeline_modules import PipelineModules
from src.orchestrator.yaml_parser import YAMLParser
from src.utils.settings import INPUTS, NAME, OBJECT, OUTPUTS


class Orchestrator:
    def __init__(self, yaml_parser: YAMLParser, pipeline_modules: PipelineModules) -> None:
        self._yaml_parser = yaml_parser
        self._pipeline_modules = pipeline_modules

        self._pipeline_elements = []
        self._outputs = {}

    def initialize_pipeline_elements(self, pipeline_definition_file: Path) -> None:
        try:
            pipeline_definition = self._yaml_parser.get_pipeline_definition(
                pipeline_definition_file=pipeline_definition_file
            )

            pipeline_elements_modules = self._pipeline_modules.get_all_pipeline_element_modules()

            for element in pipeline_definition:
                element_class = self._pipeline_modules.get_pipeline_element_class(
                    modules=pipeline_elements_modules, class_name=element[NAME]
                )
                element[OBJECT] = element_class(settings=element.get("settings", None))
        except (KeyError, ModuleNotFoundError, ImportError) as e:
            message = f"Pipeline elements modules discovery failed {e}"
            logging.exception(message)
            sys.exit(message)
        else:
            self._pipeline_elements = pipeline_definition

    @run_exception
    def run_pipeline_element(self) -> None:
        for element in self._pipeline_elements:
            element[INPUTS].update(self._outputs)
            outputs = element[OBJECT].run(inputs=element[INPUTS], outputs=element.get(OUTPUTS))
            self._validate_pipeline_element(element=element, outputs=outputs)
            self._outputs.update(outputs)

    @staticmethod
    def _validate_pipeline_element(element: Dict[str, Any], outputs: Any) -> None:
        if (element.get(OUTPUTS, None) is not None and outputs == {}) or (
            element.get(OUTPUTS, None) is None and outputs != {}
        ):
            raise ValueError(
                f"The pipeline element {element['name']} either definition or implementation is incorrect."
                f"Please check that {OUTPUTS} added to the definition or they are returned from the run method."
            )

    def cleanup(self) -> None:
        for element in self._pipeline_elements:
            element[OBJECT].cleanup(outputs=element.get(OUTPUTS))
