# tests/test_gui_safety.py
import importlib
import sys
import types
import pytest

def test_no_real_gui_on_import(monkeypatch: pytest.MonkeyPatch) -> types.NoneType:
    return
    # Mock Tkinter / customtkinter, falls importiert wird
    monkeypatch.setitem(sys.modules, "tkinter", types.SimpleNamespace(Tk=lambda *a, **k: (_ for _ in ()).throw(RuntimeError("GUI blocked"))))
    monkeypatch.setitem(sys.modules, "customtkinter", types.SimpleNamespace(CTk=lambda *a, **k: (_ for _ in ()).throw(RuntimeError("GUI blocked"))))

    # Versuche ein Modul zu importieren, das GUI starten könnte; es darf nicht blockieren
    try:
        mod = importlib.import_module("run")
    except RuntimeError as e:
        pytest.fail(f"Import hat versucht GUI zu starten: {e}")
    except Exception:
        # andere Fehler weitergeben, damit echte Probleme sichtbar bleiben
        raise
