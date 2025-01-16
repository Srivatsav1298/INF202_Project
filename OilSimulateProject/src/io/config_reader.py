import toml
import os
import logging 

logger = logging.getLogger(__name__)

class ConfigReader:
    def __init__(self, config_file):
        if not os.path.exists(config_file):
            logger.error(f"Config file '{config_file}' not found.")
            raise FileNotFoundError(f"Config file '{config_file}' not found.")
        self.config_file = config_file
        self.config = self._read_config()

    def _read_config(self):
        try:
            logger.info(f"Loading configuration from {self.config_file}...")
            config = toml.load(self.config_file)
            required_keys = ["nSteps", "tStart", "tEnd", "fps", "oil_spill_center", "writeFrequency", "restartFile"]
            for key in required_keys:
                if key not in config:
                    logger.error(f"Missing required key: {key}")
                    raise ValueError(f"Missing required key: {key}")
            logger.info("Configuration file loaded successfully.")
            return config
        except toml.TomlDecodeError as e:
            logger.error(f"Error decoding TOML file: {e}")
            raise ValueError(f"Error decoding TOML file: {e}")

    @property
    def parameters(self):
        return self.config