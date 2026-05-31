import asyncio
import threading
from typing import Any

import pytest
from asyncclick import ClickException

from tortoise_cli import cli as cli_module


def test_embed_interactive_shell_prefers_ipython(monkeypatch):
    calls = []
    namespace = {"Tortoise": object()}
    tortoise_config = {"connections": {"default": "sqlite://:memory:"}}

    async def fake_ipython(ns, config, generate_schemas):
        calls.append(("ipython", ns, config, generate_schemas))

    async def fake_ptpython(ns, config, generate_schemas):
        calls.append(("ptpython", ns, config, generate_schemas))

    monkeypatch.setattr(cli_module, "_has_module", lambda name: name in {"IPython", "ptpython"})
    monkeypatch.setattr(cli_module, "_embed_ipython", fake_ipython)
    monkeypatch.setattr(cli_module, "_embed_ptpython", fake_ptpython)

    asyncio.run(cli_module._embed_interactive_shell(namespace, tortoise_config, True))

    assert calls == [("ipython", namespace, tortoise_config, True)]


def test_embed_ipython_uses_one_thread_loop_for_tortoise_and_cells(monkeypatch):
    calls: list[Any] = []
    loops: list[Any] = []
    namespace = {"Tortoise": object()}
    tortoise_config = {"connections": {"default": "sqlite://:memory:"}}
    main_thread = threading.get_ident()

    class FakeTortoiseContext:
        def __enter__(self):
            calls.append(("context_enter", threading.get_ident()))
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            calls.append(("context_exit", threading.get_ident()))

        async def close_connections(self):
            calls.append(("close", asyncio.get_running_loop(), threading.get_ident()))

    async def fake_init(config, generate_schemas):
        loops.append(("init", asyncio.get_running_loop(), threading.get_ident()))
        calls.append(("init", config, generate_schemas))
        return FakeTortoiseContext()

    def fake_embed(**kwargs):
        async def fake_cell():
            loops.append(("cell", asyncio.get_running_loop(), threading.get_ident()))
            return "ok"

        runner_result = kwargs["loop_runner"](fake_cell())
        calls.append(("embed", kwargs, threading.get_ident() != main_thread, runner_result))
        asyncio.run(asyncio.sleep(0))

    monkeypatch.setattr(cli_module, "_init_tortoise", fake_init)
    monkeypatch.setattr(
        cli_module.importlib,
        "import_module",
        lambda name: type("FakeIPython", (), {"embed": fake_embed}),
    )

    asyncio.run(cli_module._embed_ipython(namespace, tortoise_config, True))

    assert calls[0] == ("init", tortoise_config, True)
    _, kwargs, ran_in_thread, runner_result = next(call for call in calls if call[0] == "embed")
    assert kwargs["autoawait"] is True
    assert kwargs["header"] == "Tortoise Shell"
    assert callable(kwargs["loop_runner"])
    assert kwargs["using"] is None
    assert kwargs["user_ns"] is namespace
    assert ran_in_thread is True
    assert runner_result == "ok"
    assert [call[0] for call in calls].count("context_enter") == 2
    assert [call[0] for call in calls].count("context_exit") == 2
    assert calls[-2][0] == "close"
    assert loops[0][1] is loops[1][1]
    assert loops[0][2] == loops[1][2] != main_thread


def test_embed_interactive_shell_uses_ptpython_when_ipython_is_missing(monkeypatch):
    calls = []
    namespace = {"Tortoise": object()}
    tortoise_config = {"connections": {"default": "sqlite://:memory:"}}

    async def fake_ipython(ns, config, generate_schemas):
        calls.append(("ipython", ns, config, generate_schemas))

    async def fake_ptpython(ns, config, generate_schemas):
        calls.append(("ptpython", ns, config, generate_schemas))

    monkeypatch.setattr(cli_module, "_has_module", lambda name: name == "ptpython")
    monkeypatch.setattr(cli_module, "_embed_ipython", fake_ipython)
    monkeypatch.setattr(cli_module, "_embed_ptpython", fake_ptpython)

    asyncio.run(cli_module._embed_interactive_shell(namespace, tortoise_config, False))

    assert calls == [("ptpython", namespace, tortoise_config, False)]


def test_embed_interactive_shell_errors_without_backend(monkeypatch):
    monkeypatch.setattr(cli_module, "_has_module", lambda name: False)

    with pytest.raises(ClickException, match="No interactive shell backend installed"):
        asyncio.run(cli_module._embed_interactive_shell({}, {}, False))
