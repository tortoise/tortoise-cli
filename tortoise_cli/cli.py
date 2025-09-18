from __future__ import annotations

import contextlib
import platform
import sys
from collections.abc import AsyncGenerator

import asyncclick as click
from ptpython.repl import embed
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


if platform.system() == "Windows":
    _patch_loop_factory_for_ptpython()


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
    await Tortoise.init(config=tortoise_config)
    if generate_schemas is None:
        cons = tortoise_config["connections"]
        # Auto generate schemas when flag not explicitly passed and dialect is sqlite
        generate_schemas = "sqlite" in str(cons.get("default", cons))
    if generate_schemas:
        await Tortoise.generate_schemas(safe=True)


@cli.command(help="Start a interactive shell.")
@click.pass_context
async def shell(ctx: click.Context) -> None:
    async with aclose_tortoise():
        with contextlib.suppress(EOFError, ValueError):
            await embed(
                globals=globals(),
                title="Tortoise Shell",
                vi_mode=True,
                return_asyncio_coroutine=True,
                patch_stdout=True,
            )


def main() -> None:
    if sys.path[0] != ".":
        sys.path.insert(0, ".")
    cli()


if __name__ == "__main__":
    main()
