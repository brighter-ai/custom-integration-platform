import importlib
import inspect
from pathlib import Path
from typing import Any, Dict

PY = ".py"
DUNDER = "__"


class PipelineModules:
    def __init__(self, modules_path: Path, working_directory: Path) -> None:
        self._modules_path = modules_path
        self._working_directory = working_directory

    def get_all_pipeline_element_modules(self) -> Dict[str, str]:
        modules = {}

        for item in self._modules_path.rglob("*"):
            if item.is_file() and item.suffix == PY and DUNDER not in item.stem:
                module_relative_path = str(item.relative_to(self._working_directory))
                modules[item.stem.replace("_", "")] = module_relative_path.replace("/", ".").replace(PY, "")

        if modules == {}:
            raise ModuleNotFoundError(
                f"No pipeline elements modules were found. "
                f"Please check if you added them into the {self._modules_path} directory."
            )

        return modules

    @staticmethod
    def get_pipeline_element_class(modules: Dict[str, str], class_name: str) -> Any:
        if not (module := modules.get(class_name.lower(), None)):
            raise KeyError(f"Class name '{class_name}' is not found in the pipeline elements modules.")

        element_module = importlib.import_module(module)

        for name, _ in inspect.getmembers(element_module, inspect.isclass):
            if name == class_name:
                return getattr(element_module, name)

        raise ImportError("Class is not found in the module", name=class_name, path=module)
