checkfiles = tortoise_cli/ tests/ examples/ conftest.py
py_warn = PYTHONDEVMODE=1

up:
	@poetry update

deps:
	@poetry install --all-groups

style: deps _style
_style:
	ruff format $(checkfiles)
	ruff check --fix $(checkfiles)

check: deps _check
_check:
	ruff format --check $(checkfiles) || (echo "Please run 'make style' to auto-fix style issues" && false)
	ruff check $(checkfiles)
	mypy $(checkfiles)

test: deps _test
_test:
	$(py_warn) pytest

build: deps
	@poetry build

ci: check _test
