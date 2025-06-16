src_dir = tortoise_cli
checkfiles = $(src_dir) tests/ examples/ conftest.py
py_warn = PYTHONDEVMODE=1
pytest_opts = -n auto --cov=$(src_dir) --cov-append --cov-branch --tb=native -q

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
	bandit -c pyproject.toml -r $(checkfiles)
	twine check dist/*

test: deps _test
_test:
	$(py_warn) pytest $(pytest_opts)

build: deps
	@poetry build --clean

ci: build _check _test
