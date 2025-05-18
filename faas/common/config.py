import json
import os
from pathlib import Path


def load_settings():
    """Load settings from env.json if present and merge with environment variables."""
    settings = {}
    env_path = Path('env.json')
    if env_path.exists():
        try:
            with env_path.open() as f:
                data = json.load(f)
                if isinstance(data, dict):
                    settings.update({str(k): str(v) for k, v in data.items()})
        except json.JSONDecodeError:
            pass
    # Environment variables override entries in env.json
    settings.update(os.environ)
    return settings


_SETTINGS = load_settings()


def get_setting(name, default=None):
    """Retrieve a configuration value."""
    return _SETTINGS.get(name, default)
