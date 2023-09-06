import logging
import sys
from typing import Any, Dict, List, Tuple


def error_handler(error_msg: str) -> None:
    logging.error(error_msg)
    sys.exit(error_msg)


def element_main_params_specified(element: Dict[str, Any], main_params: Tuple[str]) -> bool:
    return set(main_params).issubset(set(element.keys()))


def param_has_its_value(element: Dict[str, Any]) -> bool:
    return all(element.values())


def nested_parameters_are_correct(element: Dict[str, Any], presented_nestable_params: List[str]) -> Tuple:
    for param in presented_nestable_params:
        if not isinstance(element[param], dict):
            error_handler(
                f"Parameter '{param}' of element '{element['name']}' "
                f"should be a dict (should contain nested parameters "
                f"with their values)"
            )

        if wrong_parameter_nesting(element, param):
            error_handler(
                f"Some of the nested parameters of '{param}' of element "
                f"'{element['name']}' mistakenly contain nested params"
            )


def wrong_parameter_nesting(pipeline_element: Dict[str, Any], param_to_check: str) -> bool:
    return any(isinstance(value, dict) for value in pipeline_element[param_to_check].values())
