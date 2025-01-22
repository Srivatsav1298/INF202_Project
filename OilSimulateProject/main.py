import time
import logging
import os
import argparse
from pathlib import Path

from src.io.mesh_reader import Mesh
from src.simulation.simulator import Simulation
from src.io.config_reader import (
    load_single_config_file,
    load_all_configs_in_folder
)

def setup_logging(log_filename: str = 'default.log', level: int = logging.INFO) -> logging.Logger:
    """
    Sets up logging for the application. Logs are written to both the console (if enabled) and a file.

    Args:
        log_filename (str): Name of the log file to write logs to.
        level (int): Logging level (e.g., logging.INFO or logging.DEBUG).

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger()
    logger.setLevel(level)

    # Avoid stacking handlers when this function. is called multiple times.
    if logger.hasHandlers():
        logger.handlers.clear()

    # File handler for writing logs to a file
    fh = logging.FileHandler(log_filename, mode='w')
    fh.setLevel(level)
    fh.setFormatter(logging.Formatter('[%(levelname)s] - %(message)s'))
    logger.addHandler(fh)

    return logger

def run_simulation_for_config(config: dict, config_filename: str) -> None:
    """
    Runs the simulation for a given configuration file.

    Args:
        config (dict): Parsed configuration dictionary.
        config_filename (str): Name of the configuration file being used.
    """
    logger = logging.getLogger(__name__)

    # Prepare the results folder for this config
    config_basename = os.path.splitext(config_filename)[0]
    results_folder = Path("results") / config_basename
    results_folder.mkdir(parents=True, exist_ok=True)  # Create folder if it doesn't exist.

    # Determine log file name based on config or use default.
    log_name = config["IO"].get("logName", "logfile")
    log_file_path = results_folder / f"{log_name}.log"
    setup_logging(log_filename=str(log_file_path), level=logging.INFO)

    print(f"\n--- Running simulation for config file: '{config_filename}' ---")
    logger.info(f"--- Running simulation for config file: '{config_filename}' ---")

    # Log the configuration details for transparency
    logger.info("### Simulation Parameters ###")
    for section, params in config.items():
        logger.info(f"[{section}]")
        for key, value in params.items():
            logger.info(f"  {key} = {value}")

    # Extract simulation settings
    n_steps = config["settings"]["nSteps"]
    t_start = config["settings"]["tStart"]
    t_end = config["settings"]["tEnd"]

    geometry = config["geometry"]
    mesh_name = geometry["meshName"]
    oil_spill_center = geometry["oilSpillCenter"]
    fishing_grounds = geometry["borders"]

    io_section = config["IO"]
    write_frequency = io_section.get("writeFrequency")
    restart_file = io_section.get("restartFile")

    if write_frequency is None:
        logger.info("No write frequency specified. Video output will not be generated.")
    else:
        logger.info(f"Video output frequency set to: {write_frequency}")

    if restart_file is not None:
        logger.info(f"Restart file provided: {restart_file}")

    # Measure execution time
    start_time = time.time()

    # Load the simulation mesh.
    file_path = f"data/mesh/{mesh_name}"
    mesh = Mesh(file_path)

    # Initialize and run the simulator
    sim = Simulation(
        mesh,
        oil_spill_center,
        fishing_grounds,
        n_steps,
        t_start,
        t_end,
        write_frequency,
        results_folder,
        restart_file,
        config_basename
    )

    sim.run_simulation()

    elapsed = time.time() - start_time
    logger.info(f"Execution time for '{config_filename}': {elapsed:.2f} seconds\n")

def main() -> None:
    """
    Main entry point for the simulation script. Parses command-line arguments and runs simulations accordingly.
    """
    parser = argparse.ArgumentParser(
        description="Run the oil-spill simulation using a TOML config."
    )

    # Add argument to find all configurations or run a single one.
    parser.add_argument(
        "--find",
        nargs='?',
        const='all',
        default=None,
        help="Find all .toml config files in a folder (default: current directory)."
    )
    parser.add_argument(
        "-f", "--folder",
        type=str,
        default=None,
        help="Folder containing configuration files (default: 'config_files')."
    )
    parser.add_argument(
        "-c", "--config_file",
        type=str,
        default=None,
        help="Path to a single TOML configuration file (e.g., 'example.toml')."
    )

    args = parser.parse_args()

    if args.find == 'all':
        # Search for all configurations in the specified folder or default to current directory.
        search_folder = args.folder if args.folder else "config_files"
        configs_dict = load_all_configs_in_folder(search_folder)
        for cfg_filename, cfg in configs_dict.items():
            run_simulation_for_config(cfg, cfg_filename)
    else:
        # Handle single configuration file scenario.
        if args.config_file:
            # Resolve the file path relative to the folder if provided.
            config_path = os.path.join(args.folder, args.config_file) if args.folder else args.config_file
        else:
            # Default to 'input.toml' in the specified folder or 'config_files'.
            default_folder = args.folder if args.folder else "config_files"
            config_path = os.path.join(default_folder, "input.toml")

        # Load and run the single configuration file.
        single_config = load_single_config_file(config_path)
        run_simulation_for_config(single_config, os.path.basename(config_path))

if __name__ == "__main__":
    main()