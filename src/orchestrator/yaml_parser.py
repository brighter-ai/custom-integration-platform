import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import yaml

from src.utils.settings import INPUTS, NAME, OUTPUTS, SETTINGS
from src.utils.utils import (
    element_main_params_specified,
    error_handler,
    nested_parameters_are_correct,
    param_has_its_value,
)


class YAMLParser:
    def __init__(
        self,
        pipeline_title: str = "elements",
        main_params: Tuple[str] = (NAME, INPUTS),
        nested_params: Tuple[str] = (INPUTS, OUTPUTS, SETTINGS),
    ) -> None:
        self.pipeline_title = pipeline_title
        self.main_params = main_params
        self.nested_params = nested_params

    def get_pipeline_definition(self, pipeline_definition_file: Path) -> List[Dict]:
        pipeline = self._load_pipeline_definition(pipeline_definition_file)
        self._is_pipeline_definition_correct(pipeline)
        return pipeline

    def _load_pipeline_definition(self, pipeline_definition_file: Path) -> List[Dict]:
        with pipeline_definition_file.open() as f:
            try:
                yaml_obj = yaml.safe_load(f)
                pipeline = yaml_obj[self.pipeline_title]
            except Exception as e:
                logging.exception(e)
                sys.exit(str(e))
        return pipeline

    def _is_pipeline_definition_correct(self, pipeline: List[Dict]) -> None:
        if not isinstance(pipeline, list):
            error_handler("Pipeline definition must be a list of elements")

        for idx, element in enumerate(pipeline):
            if not isinstance(element, dict):
                error_handler(f"Pipeline element {idx} ('{element}') must be a dict.")

            if not element_main_params_specified(element, self.main_params):
                error_handler(
                    f"Problem with {idx} element - every element should "
                    f"contain at least following parameters: {self.main_params} "
                    f"and optionally 'outputs', 'settings'. But has only {list(element.keys())}"
                )

            if not param_has_its_value(element):
                error_handler(
                    f"Some parameters of {idx} element named '{element['name']}' are specified, "
                    f"but no values are provided"
                )

            element_nestable_params = [param for param in element.keys() if param in self.nested_params]
            nested_parameters_are_correct(element, element_nestable_params)


if __name__ == "__main__":
    pipeline_definition_file = Path("example/mp4_data_converter/src/integration_pipeline/pipeline_definition.yml")
    pipeline_list = YAMLParser().get_pipeline_definition(pipeline_definition_file=pipeline_definition_file)
