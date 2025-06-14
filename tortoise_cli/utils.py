import importlib
import os
import sys
from pathlib import Path

from asyncclick import BadOptionUsage, ClickException, Context

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomlkit as tomllib


def tortoise_orm_config(file="pyproject.toml") -> str:
    """
    get tortoise orm config from os environment variable or aerich item in pyproject.toml

    :param file: toml file that aerich item loads from it
    :return: module path and var name that store the tortoise config, e.g.: 'settings.TORTOISE_ORM'
    """
    if not (config := os.getenv("TORTOISE_ORM", "")) and (p := Path(file)).exists():
        doc = tomllib.loads(p.read_text("utf-8"))
        config = doc.get("tool", {}).get("aerich", {}).get("tortoise_orm", "")
    return config


def get_tortoise_config(ctx: Context, config: str) -> dict:
    """
    get tortoise config from module
    :param ctx:
    :param config:
    :return:
    """
    splits = config.split(".")
    config_path = ".".join(splits[:-1])
    tortoise_config = splits[-1]

    try:
        config_module = importlib.import_module(config_path)
    except ModuleNotFoundError as e:
        raise ClickException(f"Error while importing configuration module: {e}") from None

    c = getattr(config_module, tortoise_config, None)
    if not c:
        raise BadOptionUsage(
            option_name="--config",
            message=f'Can\'t get "{tortoise_config}" from module "{config_module}"',
            ctx=ctx,
        )
    return c
