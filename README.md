# tortoise-cli

[![image](https://img.shields.io/pypi/v/tortoise-cli.svg?style=flat)](https://pypi.python.org/pypi/tortoise-cli)
[![image](https://img.shields.io/github/license/tortoise/tortoise-cli)](https://github.com/tortoise/tortoise-cli)
[![image](https://github.com/tortoise/tortoise-cli/workflows/pypi/badge.svg)](https://github.com/tortoise/tortoise-cli/actions?query=workflow:pypi)

A cli tool for tortoise-orm, build on top of click and ptpython.

## Installation

You can just install from pypi.

```shell
pip install tortoise-cli
```

## Quick Start

```shell
> tortoise-cli -h                                                                                                                                                                 23:59:38
Usage: tortoise-cli [OPTIONS] COMMAND [ARGS]...

Options:
  -V, --version      Show the version and exit.
  -c, --config TEXT  TortoiseORM config dictionary path, like
                     settings.TORTOISE_ORM
  -h, --help         Show this message and exit.

Commands:
  shell  Start an interactive shell.
```

## Usage

First, you need make a TortoiseORM config object, assuming that in `settings.py`.

```python
TORTOISE_ORM = {
    "connections": {
        "default": "sqlite://:memory:",
    },
    "apps": {
        "models": {"models": ["examples.models"], "default_connection": "default"},
    },
}
```

## Interactive shell

![image](https://raw.githubusercontent.com/tortoise/tortoise-cli/main/images/shell.png)

Then you can start an interactive shell for TortoiseORM.

```shell
tortoise-cli -c settings.TORTOISE_ORM shell
```

Or you can set config by set environment variable.

```shell
export TORTOISE_ORM=settings.TORTOISE_ORM
```

Then just run:

```shell
tortoise-cli shell
```

## License

This project is licensed under the
[Apache-2.0](https://github.com/tortoise/tortoise-cli/blob/main/LICENSE) License.
