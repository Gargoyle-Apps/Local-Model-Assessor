"""Unit tests for sweep-ide-config.py helpers."""

import importlib.util
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"


def _load_script(name: str):
    module_name = name.replace("-", "_").removesuffix(".py")
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, SCRIPTS_DIR / name)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


mod = _load_script("sweep-ide-config.py")


class TestDetectTargets:
    def test_continue_from_primary_agent(self):
        profile = {"primary_agent": {"name": "Continue"}}
        assert mod.detect_targets(profile) == ["continue"]

    def test_cline_and_roo(self):
        assert mod.detect_targets({"primary_agent": {"name": "Cline"}}) == ["cline"]
        assert mod.detect_targets({"primary_agent": {"name": "Roo Code"}}) == ["cline"]

    def test_optional_agents(self):
        profile = {
            "primary_agent": {"name": "Cursor"},
            "optional_agents": [{"name": "Continue"}],
        }
        assert mod.detect_targets(profile) == ["continue"]

    def test_explicit_override(self):
        profile = {"primary_agent": {"name": "Continue"}}
        assert mod.detect_targets(profile, explicit=["cline"]) == ["cline"]

    def test_fallback_all_when_unrecognized(self):
        profile = {"primary_agent": {"name": "Your Primary Agent"}}
        assert mod.detect_targets(profile) == ["continue", "cline"]
