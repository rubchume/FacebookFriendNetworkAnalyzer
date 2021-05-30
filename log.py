import logging.config
from pathlib import Path
import yaml


def configure_logging():
    root_path = Path(__file__).resolve().parent

    with open(root_path.joinpath("setup_logger.yaml"), 'r') as f:
        config = yaml.safe_load(f.read())

        for handler_name, handler in config["handlers"].items():
            if handler_name.startswith("file_"):
                handler["filename"] = root_path.joinpath(handler["filename"])

        logging.config.dictConfig(config)
