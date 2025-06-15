import os
from pathlib import Path
from unittest.mock import patch

import pytest
from asyncclick.exceptions import ClickException

import examples
from tortoise_cli.utils import get_tortoise_config, tortoise_orm_config


def test_tortoise_orm_config():
    assert tortoise_orm_config() == "examples.TORTOISE_ORM"
    with patch.dict(os.environ, {"TORTOISE_ORM": "app.settings.TORTOISE_ORM"}):
        assert tortoise_orm_config() == "app.settings.TORTOISE_ORM"
    with patch.object(Path, "read_text", return_value=""):
        assert tortoise_orm_config() == ""


def test_get_tortoise_config():
    assert get_tortoise_config(None, tortoise_orm_config()) == examples.TORTOISE_ORM  # type:ignore[arg-type]
    with pytest.raises(
        ClickException,
        match="Error while importing configuration module: No module named 'settings'",
    ):
        assert get_tortoise_config(None, "settings.TORTOISE_ORM")  # type:ignore[arg-type]
