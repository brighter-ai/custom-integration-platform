import functools
import logging
import sys
from typing import Any, Callable

from src.integration_pipeline.base.pipeline_element_exceptions import PipelineElementError, Severity


def run_exception(function: Callable) -> Callable:
    @functools.wraps(function)
    def wrapper(*args, **kwargs) -> Any:
        try:
            result = function(*args, **kwargs)

            return result
        except PipelineElementError as e:
            element_message = "the pipeline element raised an exception"
            logging.exception(f"{element_message}: {e.log_message}")

            match e.severity:
                case Severity.major:
                    sys.exit(f"{element_message}: {e.public_message}")

                case Severity.minor:
                    pass

                case _:
                    raise TypeError(
                        f"{element_message} with unknown severity: {e.public_message}. "
                        f"Please check the element's implementation"
                    )

    return wrapper
