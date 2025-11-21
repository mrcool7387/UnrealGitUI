# tests/test_imports.py
import importlib
import os
import pytest

REQUIRED_MODULES: list[str] = [
    "run",            # run.py im repo root
    "main",           # falls es ein main package gibt
]

def test_required_files_exist() -> None:
    repo_root: str = os.path.dirname(os.path.dirname(__file__))
    # falls tests in repo/tests liegen, reicht das, ansonsten anpassen
    assert os.path.exists(os.path.join(repo_root, "README.md")), "README.md fehlt"
    assert os.path.exists(os.path.join(repo_root, "pyproject.toml")), "pyproject.toml fehlt"

@pytest.mark.parametrize("modname", REQUIRED_MODULES)
def test_module_importable(modname: str) -> None:
    # versuche das Modul zu importieren, fehlschlag zeigt Syntax-/Importfehler
    try:
        importlib.import_module(modname)
    except Exception as e:
        pytest.fail(f"Import von {modname} schlug fehl: {e}")
