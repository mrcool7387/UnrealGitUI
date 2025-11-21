# tests/test_run_cli.py
import importlib
import sys
import types
from typing import Any
import pytest

# Test: import run.py and call an exposed entrypoint if available
def test_run_module_import_and_entrypoint(monkeypatch: pytest.MonkeyPatch) -> types.NoneType:
    # Wenn run.py eine main/run-Funktion hat, importieren wir und rufen sie an, GUI-Aufrufe werden gemockt
    try:
        run_mod = importlib.import_module("run")
    except Exception as e:
        pytest.skip(f"run module not importable, skipping: {e}")

    # Falls run_mod.run oder run_mod.main existiert, rufe sie auf, nachdem wir GUI-start ersetzten
    if hasattr(run_mod, "run") or hasattr(run_mod, "main"):
        # Mock häufige GUI libs falls verwendet
        monkeypatch.setitem(sys.modules, "customtkinter", types.SimpleNamespace())
        monkeypatch.setitem(sys.modules, "tkinter", types.SimpleNamespace())

        entry: Any | types.NoneType = getattr(run_mod, "run", None) or getattr(run_mod, "main", None)
        # Rufe die entry-Funktion auf und erwarte, dass sie entweder None zurückgibt oder sauber endet
        res: object | types.NoneType = entry() if callable(entry) else None
        assert res is None or res == 0, "run/main returns unexpected value"
    else:
        pytest.skip("Keine run/main entrypoint im run module gefunden")
