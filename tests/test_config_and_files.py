# tests/test_config_and_files.py
import os
import tomllib
from typing import Any

def test_pyproject_contains_basic_metadata() -> Any:
    root: str = os.path.dirname(os.path.dirname(__file__))
    pyproject: str = os.path.join(root, "pyproject.toml")
    assert os.path.exists(pyproject), "pyproject.toml fehlt"
    with open(pyproject, "rb") as f:
        data: dict[str, Any] = tomllib.load(f)
    # check for common metadata keys, passe an falls andere toolchain genutzt wird
    assert isinstance(data, dict)
    # Beispielprüfungen
    assert any(k in data for k in ("project", "tool")), "pyproject.toml enthält keine 'project' oder 'tool' Sektion"

def test_readme_has_short_description() -> None:
    root: str = os.path.dirname(os.path.dirname(__file__))
    readme: str = os.path.join(root, "README.md")
    assert os.path.exists(readme), "README.md fehlt"
    with open(readme, "r", encoding="utf-8") as f:
        txt: str = f.read()
    assert len(txt) > 10, "README.md scheint ungewöhnlich kurz"
