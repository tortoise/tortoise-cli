import asyncio

import pytest
from asyncclick import ClickException

from tortoise_cli import cli as cli_module


def test_embed_interactive_shell_prefers_ipython(monkeypatch):
    calls = []
    namespace = {"Tortoise": object()}

    async def fake_ipython(ns):
        calls.append(("ipython", ns))

    async def fake_ptpython(ns):
        calls.append(("ptpython", ns))

    monkeypatch.setattr(cli_module, "_has_module", lambda name: name in {"IPython", "ptpython"})
    monkeypatch.setattr(cli_module, "_embed_ipython", fake_ipython)
    monkeypatch.setattr(cli_module, "_embed_ptpython", fake_ptpython)

    asyncio.run(cli_module._embed_interactive_shell(namespace))

    assert calls == [("ipython", namespace)]


def test_embed_interactive_shell_uses_ptpython_when_ipython_is_missing(monkeypatch):
    calls = []
    namespace = {"Tortoise": object()}

    async def fake_ipython(ns):
        calls.append(("ipython", ns))

    async def fake_ptpython(ns):
        calls.append(("ptpython", ns))

    monkeypatch.setattr(cli_module, "_has_module", lambda name: name == "ptpython")
    monkeypatch.setattr(cli_module, "_embed_ipython", fake_ipython)
    monkeypatch.setattr(cli_module, "_embed_ptpython", fake_ptpython)

    asyncio.run(cli_module._embed_interactive_shell(namespace))

    assert calls == [("ptpython", namespace)]


def test_embed_interactive_shell_errors_without_backend(monkeypatch):
    monkeypatch.setattr(cli_module, "_has_module", lambda name: False)

    with pytest.raises(ClickException, match="No interactive shell backend installed"):
        asyncio.run(cli_module._embed_interactive_shell({}))
