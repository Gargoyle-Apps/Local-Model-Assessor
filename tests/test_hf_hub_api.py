"""Tests for hf-hub-api.py (mocked HTTP)."""

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"


def _load_script(name: str):
    module_name = name.replace("-", "_").removesuffix(".py")
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, SCRIPTS_DIR / name)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


mod = _load_script("hf-hub-api.py")


class _FakeResponse:
    def __init__(self, body, headers=None):
        self._body = body if isinstance(body, bytes) else body.encode()
        self.headers = headers or {}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self._body


def _fake_json_response(data, link=None):
    headers = {}
    if link:
        headers["Link"] = f'<{link}>; rel="next"'
    return _FakeResponse(json.dumps(data).encode(), headers)


def test_collection_item_count_from_items():
    assert mod.collection_item_count({"items": [1, 2, 3]}) == 3


def test_collection_item_count_from_item_count():
    assert mod.collection_item_count({"itemCount": 7}) == 7


def test_paginate_single_page():
    with patch.object(mod.urllib.request, "urlopen") as mock_open:
        mock_open.return_value = _fake_json_response([{"slug": "a"}, {"slug": "b"}])
        result = mod.paginate("/collections", {"owner": "mlx-community", "limit": 100})
    assert len(result) == 2


def test_paginate_follows_next_link():
    page1 = [{"slug": "a"}]
    page2 = [{"slug": "b"}]

    def side_effect(req, timeout=30.0):
        url = req.full_url
        if "cursor=" not in url:
            return _fake_json_response(
                page1,
                link="https://huggingface.co/api/collections?owner=mlx-community&limit=1&cursor=abc",
            )
        return _fake_json_response(page2)

    with patch.object(mod.urllib.request, "urlopen", side_effect=side_effect):
        result = mod.paginate("/collections", {"owner": "mlx-community", "limit": 1})

    assert [r["slug"] for r in result] == ["a", "b"]


def test_list_models_truncates_to_limit():
    models = [{"id": f"m{i}"} for i in range(5)]
    with patch.object(mod.urllib.request, "urlopen") as mock_open:
        mock_open.return_value = _fake_json_response(models)
        result = mod.list_models(author="mlx-community", limit=3)
    assert len(result) == 3
    assert result[0]["id"] == "m0"
