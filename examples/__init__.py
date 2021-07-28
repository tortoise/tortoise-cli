TORTOISE_ORM = {
    "connections": {
        "default": "sqlite://:memory:",
    },
    "apps": {
        "models": {"models": ["examples.models"], "default_connection": "default"},
    },
}
