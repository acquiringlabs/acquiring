import enum
import importlib.util
import inspect
import os
from typing import Protocol
from django_acquiring.protocols.repositories import AbstractRepository


def test_allProtocolFilesContainSubclassesOfDecoratorProtocolOrEnum():
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    django_acquiring_dir = os.path.join(project_dir, "django_acquiring")
    for root, dirs, files in os.walk(django_acquiring_dir):
        for file in files:
            if "protocols" in root.split(os.path.sep):  # in protocols folder
                file_path = os.path.join(root, file)
                module_name = os.path.splitext(os.path.basename(file_path))[0]
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and obj.__module__ == module_name:  # A non-imported class
                        assert issubclass(obj, Protocol) or issubclass(
                            obj, enum.Enum
                        ), f"class {name} is neither a Protocol nor an Enum"
                    elif inspect.isfunction(obj) and obj.__module__ == module_name:  # A non-imported function
                        assert hasattr(obj, "__call__"), f"function {name} is not a decorator"


def test_allRepositoryFilesContainSubclassesOfAbstractRepository():
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    django_acquiring_dir = os.path.join(project_dir, "django_acquiring")
    for root, dirs, files in os.walk(django_acquiring_dir):
        for file in files:
            if file.endswith("repositories.py"):
                file_path = os.path.join(root, file)
                module_name = os.path.splitext(os.path.basename(file_path))[0]
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and obj.__module__ == module_name:  # A non-imported class
                        assert issubclass(obj, AbstractRepository), f"class {name} is not a repository"
