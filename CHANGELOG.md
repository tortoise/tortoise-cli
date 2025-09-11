# ChangeLog

## 0.2

### 0.2.0

- feat: migrate from poetry to uv
- ci: activate ci workflow and add test for utils (#8)
- feat: generate schemas optionally ([#7])
- Use `asyncclick` instead of `click` ([#6])
- Only install tomlkit for Python version less than 3.11 ([#5])
- Migrate lint tool from isort+black to ruff ([#5])
- Drop support for Python3.8 ([#4])

[#8]: https://github.com/tortoise/tortoise-cli/pull/8
[#7]: https://github.com/tortoise/tortoise-cli/pull/7
[#6]: https://github.com/tortoise/tortoise-cli/pull/6
[#5]: https://github.com/tortoise/tortoise-cli/pull/5
[#4]: https://github.com/tortoise/tortoise-cli/pull/4

## 0.1

### 0.1.2

- Can read config from config of aerich.

### 0.1.1

- Add `sys.path.insert(0,'.')`.

### 0.1.0

- First release.
