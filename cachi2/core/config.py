from pathlib import Path

import yaml
from pydantic import BaseModel
from cachi2.core.errors import InvalidInput

from cachi2.core.models.input import parse_user_input


class Config(BaseModel, extra="forbid"):
    """Singleton that provides default configuration for the Cachi2 process."""

    goproxy_url: str = "https://proxy.golang.org,direct"
    default_environment_variables: dict = {
        "gomod": {"GOSUMDB": {"value": "off", "kind": "literal"}},
    }
    gomod_download_max_tries: int = 5
    gomod_strict_vendor: bool = True
    subprocess_timeout: int = 3600


_config = Config()


def get_config() -> Config:
    """Get the configuration singleton."""
    global _config
    return _config


def set_config(new_config: Config) -> None:
    """Set the configuration singleton."""
    global _config
    _config = new_config


def set_config_from_file(config_path: Path):
    """Set the configuration singleton from a YAML file."""
    try:
        data = yaml.safe_load(config_path.read_text())
    except yaml.YAMLError as e:
        raise InvalidInput(f"config file is not valid YAML: {e}")

    new_config = parse_user_input(Config.parse_obj, data)
    set_config(new_config)
