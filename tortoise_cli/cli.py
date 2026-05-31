from __future__ import annotations

import asyncio
import contextlib
import importlib
import importlib.util
import platform
import sys
from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import Any

import asyncclick as click
from tortoise import Tortoise, connections

from tortoise_cli import __version__, utils


def _patch_loop_factory_for_ptpython() -> None:
    # This patch can be removed when [prompt-toolkit/ptpython#582](https://github.com/prompt-toolkit/ptpython/issues/582) fixed
    from asyncio import get_event_loop_policy

    def do_nothing(*args, **kw) -> None: ...

    policy = get_event_loop_policy()
    if loop_factory := getattr(policy, "_loop_factory", None):
        for attr in ("add_signal_handler", "remove_signal_handler"):
            setattr(loop_factory, attr, do_nothing)


def _has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _event_loop_runner(
    loop: asyncio.AbstractEventLoop,
    tortoise_context: Any = None,
) -> Callable[[Awaitable[Any]], Any]:
    def run(coro: Awaitable[Any]) -> Any:
        context = (
            tortoise_context if hasattr(tortoise_context, "__enter__") else contextlib.nullcontext()
        )
        with context:
            return loop.run_until_complete(coro)

    return run


def _should_generate_schemas(tortoise_config: dict, generate_schemas: bool | None) -> bool:
    if generate_schemas is not None:
        return generate_schemas
    cons = tortoise_config["connections"]
    return "sqlite" in str(cons.get("default", cons))


async def _init_tortoise(tortoise_config: dict, generate_schemas: bool) -> Any:
    tortoise_context = await Tortoise.init(config=tortoise_config)
    if generate_schemas:
        await Tortoise.generate_schemas(safe=True)
    return tortoise_context


def _run_ipython_embed(
    namespace: dict[str, object],
    tortoise_config: dict,
    generate_schemas: bool,
) -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    embed = getattr(importlib.import_module("IPython"), "embed")
    tortoise_context: Any = None
    try:
        tortoise_context = loop.run_until_complete(
            _init_tortoise(tortoise_config, generate_schemas)
        )
        embed(
            autoawait=True,
            header="Tortoise Shell",
            loop_runner=_event_loop_runner(loop, tortoise_context),
            using=None,
            user_ns=namespace,
        )
    finally:
        close_connections = getattr(tortoise_context, "close_connections", None)
        if close_connections is not None and hasattr(tortoise_context, "__enter__"):
            with tortoise_context:
                loop.run_until_complete(close_connections())
        elif Tortoise._inited:
            loop.run_until_complete(connections.close_all())
        asyncio.set_event_loop(None)
        loop.close()


async def _embed_ipython(
    namespace: dict[str, object],
    tortoise_config: dict,
    generate_schemas: bool,
) -> None:
    await asyncio.to_thread(_run_ipython_embed, namespace, tortoise_config, generate_schemas)


async def _embed_ptpython(
    namespace: dict[str, object],
    tortoise_config: dict,
    generate_schemas: bool,
) -> None:
    if platform.system() == "Windows":
        _patch_loop_factory_for_ptpython()
    embed = getattr(importlib.import_module("ptpython.repl"), "embed")
    async with aclose_tortoise():
        await _init_tortoise(tortoise_config, generate_schemas)
        await embed(
            globals=namespace,
            title="Tortoise Shell",
            vi_mode=True,
            return_asyncio_coroutine=True,
            patch_stdout=True,
        )


async def _embed_interactive_shell(
    namespace: dict[str, object],
    tortoise_config: dict,
    generate_schemas: bool,
) -> None:
    if _has_module("IPython"):
        await _embed_ipython(namespace, tortoise_config, generate_schemas)
        return
    if _has_module("ptpython"):
        await _embed_ptpython(namespace, tortoise_config, generate_schemas)
        return
    raise click.ClickException(
        "No interactive shell backend installed. "
        "Install tortoise-cli[ipython] or tortoise-cli[ptpython]."
    )


@contextlib.asynccontextmanager
async def aclose_tortoise() -> AsyncGenerator[None]:
    try:
        yield
    finally:
        if Tortoise._inited:
            await connections.close_all()


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, "-V", "--version")
@click.option(
    "-c",
    "--config",
    help="TortoiseORM config dictionary path, like settings.TORTOISE_ORM",
)
@click.option(
    "--generate-schemas/--no-generate-schemas",
    default=None,
    help="Whether generate schemas after TortoiseORM inited",
)
@click.pass_context
async def cli(ctx: click.Context, config: str | None, generate_schemas: bool | None = None):
    if not config and not (config := utils.tortoise_orm_config()):
        raise click.UsageError(
            "You must specify TORTOISE_ORM in option or env, or config file pyproject.toml from config of aerich",
            ctx=ctx,
        )
    tortoise_config = utils.get_tortoise_config(ctx, config)
    ctx.obj = {
        "generate_schemas": _should_generate_schemas(tortoise_config, generate_schemas),
        "tortoise_config": tortoise_config,
    }


@cli.command(help="Start a interactive shell.")
@click.pass_context
async def shell(ctx: click.Context) -> None:
    with contextlib.suppress(EOFError, ValueError):
        await _embed_interactive_shell(
            globals(),
            ctx.obj["tortoise_config"],
            ctx.obj["generate_schemas"],
        )


def main() -> None:
    if sys.path[0] != ".":
        sys.path.insert(0, ".")
    cli()


if __name__ == "__main__":
    main()
