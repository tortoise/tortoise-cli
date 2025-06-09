import importlib

from click import BadOptionUsage, ClickException, Context


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
