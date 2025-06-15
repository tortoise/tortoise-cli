import os
from pathlib import Path
from unittest.mock import patch

import pytest
from asyncclick import BadOptionUsage, ClickException, Command, Context

import examples
from tortoise_cli.utils import get_tortoise_config, tortoise_orm_config

EMPTY_TORTOISE_ORM = None


def test_tortoise_orm_config():
    assert tortoise_orm_config() == "examples.TORTOISE_ORM"
    with patch.dict(os.environ, {"TORTOISE_ORM": "app.settings.TORTOISE_ORM"}):
        assert tortoise_orm_config() == "app.settings.TORTOISE_ORM"
    with patch.object(Path, "read_text", return_value=""):
        assert tortoise_orm_config() == ""


def test_get_tortoise_config():
    ctx = Context(Command("shell"))
    assert get_tortoise_config(ctx, tortoise_orm_config()) == examples.TORTOISE_ORM
    with pytest.raises(
        ClickException,
        match="Error while importing configuration module: No module named 'settings'",
    ):
        assert get_tortoise_config(ctx, "settings.TORTOISE_ORM")
    with pytest.raises(BadOptionUsage):
        assert get_tortoise_config(ctx, "tests.test_utils.EMPTY_TORTOISE_ORM")
