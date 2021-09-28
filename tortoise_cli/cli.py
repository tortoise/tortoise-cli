import asyncio
import os
import sys
from functools import wraps
from pathlib import Path
from typing import Optional

import click
import tomlkit
from ptpython.repl import embed
from tortoise import Tortoise

from tortoise_cli import __version__, utils


def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(f(*args, **kwargs))
        finally:
            if f.__name__ != "cli":
                loop.run_until_complete(Tortoise.close_connections())

    return wrapper


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, "-V", "--version")
@click.option(
    "-c",
    "--config",
    help="TortoiseORM config dictionary path, like settings.TORTOISE_ORM",
)
@click.pass_context
@coro
async def cli(ctx: click.Context, config: Optional[str]):
    if not config:
        config = os.getenv("TORTOISE_ORM")
    if not config:
        file = "pyproject.toml"
        if Path(file).exists():
            with open(file, "r") as f:
                content = f.read()
            doc = tomlkit.parse(content)
            config = doc.get("tool", {}).get("aerich", {}).get("tortoise_orm")  # type:ignore
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
@coro
async def shell(ctx: click.Context):
    try:
        await embed(
            globals=globals(),
            title="Tortoise Shell",
            vi_mode=True,
            return_asyncio_coroutine=True,
            patch_stdout=True,
        )
    except (EOFError, ValueError):
        pass


def main():
    sys.path.insert(0, ".")
    cli()


if __name__ == "__main__":
    main()
