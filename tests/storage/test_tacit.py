import ast


def get_function_names(filename: str) -> set:
    """Extracts test names from a Python file."""
    with open(filename, "r") as file:
        tree = ast.parse(file.read())
        return {
            node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
        }


def test_uow_tests_are_the_same() -> None:
    test_uow_django = get_function_names("tests/storage/django/repositories/test_unit_of_work.py")
    test_uow_sqlalchemy = get_function_names("tests/storage/sqlalchemy/repositories/test_unit_of_work.py")

    assert test_uow_django == test_uow_sqlalchemy
