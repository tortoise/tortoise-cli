from __future__ import annotations

import contextlib
import os
import sys
from pathlib import Path
from collections.abc import AsyncGenerator

import asyncclick as click
from ptpython.repl import embed
from tortoise import Tortoise, connections

from tortoise_cli import __version__, utils

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomlkit as tomllib


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
@click.pass_context
async def cli(ctx: click.Context, config: str | None):
    if (
        not config
        and not (config := os.getenv("TORTOISE_ORM"))
        and (p := Path("pyproject.toml")).exists()
    ):
        doc = tomllib.loads(p.read_text("utf-8"))
        config = doc.get("tool", {}).get("aerich", {}).get("tortoise_orm", "")
    if not config:
        raise click.UsageError(
            "You must specify TORTOISE_ORM in option or env, or config file pyproject.toml from config of aerich",
            ctx=ctx,
        )
    tortoise_config = utils.get_tortoise_config(ctx, config)
    await Tortoise.init(config=tortoise_config)
    await Tortoise.generate_schemas(safe=True)


@cli.command(help="Start a interactive shell.")
@click.pass_context
async def shell(ctx: click.Context):
    async with aclose_tortoise():
        with contextlib.suppress(EOFError, ValueError):
            await embed(
                globals=globals(),
                title="Tortoise Shell",
                vi_mode=True,
                return_asyncio_coroutine=True,
                patch_stdout=True,
            )


def main():
    if sys.path[0] != ".":
        sys.path.insert(0, ".")
    cli()


if __name__ == "__main__":
    main()
