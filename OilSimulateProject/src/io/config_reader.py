import os
import tomllib
import logging
from typing import Dict

logger = logging.getLogger(__name__)

# Required top-level sections in the TOML file
REQUIRED_TOP_LEVEL_KEYS = ["settings", "geometry"]

# Required keys
REQUIRED_SETTINGS_KEYS = ["nSteps", "tEnd"]  # tStart required if restart file is provided
REQUIRED_GEOMETRY_KEYS = ["meshName", "oilSpillCenter", "borders"]

def read_toml_file(filepath: str) -> Dict:
    """
    Reads a TOML file and returns its contents as a dictionary.

    Args:
        filepath (str): Path to the TOML file.

    Returns:
        Dict: Parsed content of the TOML file.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the TOML file cannot be parsed.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "rb") as f:
        try:
            config = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            raise ValueError(f"Error parsing TOML file {filepath}: {e}")

    logger.debug(f"Successfully read TOML file: {filepath}")
    return config

def validate_and_fill_defaults(config: Dict, filepath: str) -> Dict:
    """
    Validates the configuration dictionary against required keys and sections.
    Adds default values for optional keys when necessary.

    Args:
        config (Dict): Configuration dictionary.
        filepath (str): Path to the TOML file (used in error messages).

    Returns:
        Dict: Validated and updated configuration dictionary.

    Raises:
        ValueError: If required keys or sections are missing, or if invalid values are provided.
    """
    # Validate top-level keys
    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in config:
            raise ValueError(f"Missing top-level section '{key}' in {filepath}.")

    # Validate and handle 'settings' section
    settings = config["settings"]
    for key in REQUIRED_SETTINGS_KEYS:
        if key not in settings:
            raise ValueError(f"Missing required 'settings.{key}' in {filepath}.")

    # Set default value for optional key 'tStart'
    settings.setdefault("tStart", 0)

    # Validate 'geometry' section
    geometry = config["geometry"]
    for key in REQUIRED_GEOMETRY_KEYS:
        if key not in geometry:
            raise ValueError(f"Missing required 'geometry.{key}' in {filepath}.")

    # Handle optional 'IO' section and set default values
    io_section = config.setdefault("IO", {})
    io_section.setdefault("logName", "logfile")

    # Check consistency between 'restartFile' and 'tStart'
    restart_file = io_section.get("restartFile")
    if restart_file is not None:
        if settings.get("tStart", 0) == 0:
            raise ValueError(
                f"Config {filepath} specifies 'restartFile' but 'tStart' is 0 (default). "
                "Explicitly set tStart to match tEnd provided in solution file."
            )
    elif settings.get("tStart", 0) != 0:
        raise ValueError(
            f"Config {filepath} specifies 'tStart' != 0 but no 'restartFile'. "
            "Both must be provided or both omitted."
        )

    return config

def load_single_config_file(filepath: str) -> Dict:
    """
    Loads and validates a single TOML configuration file.

    Args:
        filepath (str): Path to the TOML file.

    Returns:
        Dict: Validated configuration dictionary.
    """
    config = read_toml_file(filepath)
    config = validate_and_fill_defaults(config, filepath)
    logger.info(f"Loaded and validated config: {os.path.basename(filepath)}")
    return config

def load_all_configs_in_folder(folder_path: str) -> Dict[str, Dict]:
    """
    Loads and validates all TOML files in a specified folder.

    Args:
        folder_path (str): Path to the folder containing TOML files.

    Returns:
        Dict[str, Dict]: A dictionary mapping file names to their validated configurations.

    Raises:
        FileNotFoundError: If the folder does not exist or contains no TOML files.
    """
    if not os.path.isdir(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    # Find all TOML files in the folder
    toml_files = [f for f in os.listdir(folder_path) if f.endswith(".toml")]
    if not toml_files:
        raise FileNotFoundError(f"No .toml files found in folder: {folder_path}")

    configs = {}
    for file_name in toml_files:
        full_path = os.path.join(folder_path, file_name)
        configs[file_name] = load_single_config_file(full_path)

    return configs
