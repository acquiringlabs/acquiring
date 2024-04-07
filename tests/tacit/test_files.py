import enum
import importlib.util
import inspect
import os
from typing import Protocol
from acquiring import protocols


def test_allProtocolFilesContainSubclassesOfDecoratorProtocolOrEnum() -> None:
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    acquiring_dir = os.path.join(project_dir, "acquiring")
    for root, dirs, files in os.walk(acquiring_dir):
        for file in files:
            if "protocols" in root.split(os.path.sep):  # in protocols folder
                file_path = os.path.join(root, file)
                module_name = os.path.splitext(os.path.basename(file_path))[0]
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)  # type:ignore[arg-type]
                spec.loader.exec_module(module)  # type:ignore[union-attr]
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and obj.__module__ == module_name:  # A non-imported class
                        assert issubclass(
                            obj, Protocol  # type:ignore[arg-type]
                        ) or issubclass(
                            obj, enum.Enum
                        ), f"class {name} is neither a Protocol nor an Enum"
                    elif inspect.isfunction(obj) and obj.__module__ == module_name:  # A non-imported function
                        assert hasattr(obj, "__call__"), f"function {name} is not a decorator"


def test_allRepositoryFilesContainSubclassesOfAbstractRepository() -> None:
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    acquiring_dir = os.path.join(project_dir, "acquiring")
    for root, dirs, files in os.walk(acquiring_dir):
        for file in files:
            if file.endswith("repositories.py"):
                file_path = os.path.join(root, file)
                module_name = os.path.splitext(os.path.basename(file_path))[0]
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)  # type:ignore[arg-type]
                spec.loader.exec_module(module)  # type:ignore[union-attr]
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and obj.__module__ == module_name:  # A non-imported class
                        assert issubclass(obj, protocols.AbstractRepository), f"class {name} is not a repository"
