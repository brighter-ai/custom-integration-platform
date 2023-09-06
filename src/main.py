import logging
import sys
from pathlib import Path

from src.orchestrator.orchestrator import Orchestrator
from src.orchestrator.pipeline_modules import PipelineModules
from src.orchestrator.yaml_parser import YAMLParser
from src.utils.logger import configure_logging
from src.utils.settings import Settings

if __name__ == "__main__":
    configure_logging()
    logging.debug("platform started")

    settings = Settings()

    working_directory = Path.cwd()

    pipeline_modules_path = working_directory / "example" / "mp4_data_converter" / "integration_pipeline"
    pipeline_definition_file = pipeline_modules_path / "pipeline_definition.yml"

    yaml_parser = YAMLParser()

    pipeline_modules = PipelineModules(modules_path=pipeline_modules_path, working_directory=working_directory)
    orchestrator = Orchestrator(yaml_parser=yaml_parser, pipeline_modules=pipeline_modules)

    try:
        logging.info("initializing  pipeline elements")
        orchestrator.initialize_pipeline_elements(pipeline_definition_file=pipeline_definition_file)

        logging.info("running pipeline elements")
        orchestrator.run_pipeline_element()
    except Exception as e:
        message = "Unexpected error occurred"
        logging.exception(f"{message}: {e}")
        sys.exit(message)

    finally:
        orchestrator.cleanup()
