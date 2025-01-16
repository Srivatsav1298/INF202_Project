import toml
import os

class ConfigReader:
    def __init__(self, config_file):
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file '{config_file}' not found.")
        self.config_file = config_file
        self.config = self._read_config()

    def _read_config(self):
        try:
            config = toml.load(self.config_file)
            required_keys = ["nSteps", "tStart", "tEnd", "fps", "oil_spill_center", "writeFrequency", "restartFile"]
            for key in required_keys:
                if key not in config:
                    raise ValueError(f"Missing required key: {key}")
            return config
        except toml.TomlDecodeError as e:
            raise ValueError(f"Error decoding TOML file: {e}")

    @property
    def parameters(self):
        return self.config