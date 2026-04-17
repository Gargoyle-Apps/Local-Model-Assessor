"""Unit tests for helper functions in add-model-from-yaml.py."""

import importlib.util
import io
import sys
from contextlib import redirect_stderr
from pathlib import Path

import pytest

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


mod = _load_script("add-model-from-yaml.py")


class TestBuildModelfileContent:
    def test_minimal(self):
        result = mod.build_modelfile_content("llama3:8b", 4096, None, None, None)
        assert result == "FROM llama3:8b\nPARAMETER num_ctx 4096\n"

    def test_full(self):
        result = mod.build_modelfile_content(
            "llama3:8b", 8192, 0.2, 4096, "You are helpful."
        )
        assert "FROM llama3:8b" in result
        assert "PARAMETER num_ctx 8192" in result
        assert "PARAMETER temperature 0.2" in result
        assert "PARAMETER num_predict 4096" in result
        assert 'SYSTEM "You are helpful."' in result

    def test_single_line_escaping(self):
        result = mod.build_modelfile_content(
            "m:t", 4096, None, None, 'Say "hello"'
        )
        assert r'Say \"hello\"' in result

    def test_multiline_system_prompt(self):
        sp = "Line one\nLine two"
        result = mod.build_modelfile_content("m:t", 4096, None, None, sp)
        assert '"""\nLine one\nLine two\n"""' in result

    def test_triple_quote_rejection(self):
        sp = 'Line one\nContains """ triple\nLine three'
        with pytest.raises(ValueError, match="triple-quotes"):
            mod.build_modelfile_content("m:t", 4096, None, None, sp)


class TestAliasToModelfilePath:
    def test_happy_path(self):
        assert mod.alias_to_modelfile_path("llama3:8b_coding_4k") == \
            "model-data/modelfile/llama3-8b_coding_4k.mf"

    def test_path_traversal_slash(self):
        with pytest.raises(ValueError, match="path-separator"):
            mod.alias_to_modelfile_path("../../etc/passwd")

    def test_path_traversal_backslash(self):
        with pytest.raises(ValueError, match="path-separator"):
            mod.alias_to_modelfile_path("foo\\bar")

    def test_path_traversal_nul(self):
        with pytest.raises(ValueError, match="path-separator"):
            mod.alias_to_modelfile_path("foo\x00bar")


class TestLoadYaml:
    def test_raw_yaml(self):
        result = mod.load_yaml("models:\n  foo:bar:\n    vram: 8\n")
        assert "foo:bar" in result["models"]

    def test_single_fence(self):
        content = "Here is yaml:\n```yaml\nmodels:\n  a:b:\n    vram: 4\n```\n"
        result = mod.load_yaml(content)
        assert "a:b" in result["models"]

    def test_multi_fence_warning(self):
        content = (
            "```yaml\nmodels:\n  first:tag:\n    vram: 1\n```\n"
            "Some text\n"
            "```yaml\nmodels:\n  second:tag:\n    vram: 2\n```\n"
        )
        buf = io.StringIO()
        with redirect_stderr(buf):
            result = mod.load_yaml(content)
        assert "first:tag" in result["models"]
        assert "second:tag" not in result.get("models", {})
        assert "2" in buf.getvalue()
