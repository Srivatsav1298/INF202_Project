import os
import tomllib
import logging

logger = logging.getLogger(__name__)

# Required top-level sections
REQUIRED_TOP_LEVEL_KEYS = ["settings", "geometry"]

# Required keys within sections
REQUIRED_SETTINGS_KEYS = ["nSteps", "tEnd"]  # tStart is optional
REQUIRED_GEOMETRY_KEYS = ["meshName", "oilSpillCenter", "borders"]


def read_toml_file(filepath: str) -> dict:
    """
    Reads a single TOML file and returns the configuration dictionary.
    Raises FileNotFoundError if the file doesn't exist.
    Raises ValueError if the TOML cannot be parsed.
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


def validate_and_fill_defaults(config: dict, filepath: str) -> dict:
    """
    Validates that all required keys/sections are present in config.
    If optional keys are missing, sets default values.
    If something is inconsistent or missing, raise ValueError.
    """
    # --- Check top-level keys ---
    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in config:
            raise ValueError(
                f"Missing top-level section '{key}' in {filepath}."
            )

    # === SETTINGS Section ===
    settings = config["settings"]
    for key in REQUIRED_SETTINGS_KEYS:
        if key not in settings:
            raise ValueError(
                f"Missing required 'settings.{key}' in {filepath}."
            )

    # Default tStart to 0 if not present
    if "tStart" not in settings:
        settings["tStart"] = 0

    # === GEOMETRY Section ===
    geometry = config["geometry"]
    for key in REQUIRED_GEOMETRY_KEYS:
        if key not in geometry:
            raise ValueError(
                f"Missing 'geometry.{key}' in {filepath}."
            )

    # === IO Section (optional) ===
    if "IO" not in config:
        config["IO"] = {}
    io_section = config["IO"]

    # Default logName to "logfile" if missing
    if "logName" not in io_section:
        io_section["logName"] = "logfile"

    # Additional logic:
    # - If `restartFile` is provided, a tStart must be explicitly given (non-None).
    # - If `tStart` != 0 was explicitly set, we assume the user wants a restart => restartFile must exist.
    #   (Alternatively, interpret the spec to strictly require them both to appear or both absent.)
    restart_file = io_section.get("restartFile", None)

    # We check if the user actually wrote tStart in their file or not. If they never wrote it,
    # we set it to 0 above. That complicates the "vice versa" check. The simplest interpretation:
    #   "If restartFile is present, we require 'tStart' to be present in the TOML (non-default). 
    #    If tStart != 0, we also require a restartFile."
    #
    # However, the problem statement says:
    #   "If the restart file is provided, a start time must be provided and vice versa.
    #    If no start time is provided, the program automatically chooses time t=0."
    #
    # This can be interpreted as: The user must *explicitly* set a tStart if they're giving a restart file.
    # We'll do a strict check for the presence of `restartFile`.
    if restart_file is not None:
        # Check if they gave an explicit tStart in the file. We can't easily check "explicit" vs "default",
        # but at minimum let's see if they've used tStart=0 while also providing a restart file.
        # That might be allowed or not, depending on your preference. We'll assume it's not.
        if settings.get("tStart", 0) == 0:
            raise ValueError(
                f"Config {filepath} has 'restartFile' but 'tStart' is 0 (default). "
                "Please specify a valid start time for a restart."
            )
    else:
        # If no restartFile is given but tStart != 0, that's also an error.
        if settings.get("tStart", 0) != 0:
            raise ValueError(
                f"Config {filepath} has 'tStart' != 0 but no 'restartFile'. "
                "Both must be provided or both omitted."
            )

    return config


def load_single_config_file(filepath: str) -> dict:
    """
    Loads and validates a single .toml config file.
    """
    config = read_toml_file(filepath)
    config = validate_and_fill_defaults(config, filepath)
    logger.info(f"Loaded and validated config: {os.path.basename(filepath)}")
    return config


def load_all_configs_in_folder(folder_path: str) -> dict:
    """
    Scans a folder for .toml files, reads each, and returns
    {filename: config_dict} for all valid .toml's.
    Raises if folder doesn't exist or is empty of .toml files.
    """
    if not os.path.isdir(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    # Gather all .toml files
    toml_files = [f for f in os.listdir(folder_path) if f.endswith(".toml")]
    if not toml_files:
        raise FileNotFoundError(f"No .toml files found in folder: {folder_path}")

    configs = {}
    for file_name in toml_files:
        full_path = os.path.join(folder_path, file_name)
        config = load_single_config_file(full_path)
        configs[file_name] = config

    return configs
