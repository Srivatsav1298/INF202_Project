import time
import tomllib
import logging
import os
from src.io.mesh_reader import Mesh
from src.simulation.simulator import Simulation

# Set up logging to a file
log_filename = 'logfile.log'
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,  # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    handlers=[
        logging.FileHandler(log_filename),  # Log to file
        logging.StreamHandler()  # Optionally log to console
    ]
)
logger = logging.getLogger(__name__)


def load_config(filename):
    logger.info(f"Loading configuration from {filename}")
    try:
        with open(filename, 'rb') as f:
            config = tomllib.load(f)
        logger.info("Configuration loaded successfully.")
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        raise
    return config


def main(config, result_folder=None):
    start_time = time.time()
    logger.info("Starting the simulation...")

    file_path = f"data/mesh/{config['geometry']['meshName']}"
    
    try:
        # Create the mesh
        mesh = Mesh(file_path)
        logger.info(f"Mesh loaded successfully from {file_path}")
        
        # Create the simulation
        oil_spill_simulation = Simulation(mesh, config['geometry']['oilSpillCenter'], 
                                          config['geometry']['borders'], 
                                          config['settings']['nSteps'], 
                                          config['settings']['tStart'], 
                                          config['settings']['tEnd'], 
                                          config["IO"].get("writeFrequency"))
        logger.info("Simulation created successfully.")
        
        # Run the simulation
        oil_spill_simulation.run_simulation()

        # Log simulation summary
        logger.info("Simulation Summary:")
        logger.info(f"Parameters: {config}")
        logger.info("Oil amounts in fishing grounds over time logged above.")

    except Exception as e:
        logger.error(f"Error occurred during simulation setup: {e}")
        return

    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"Execution time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    # Generate result folder based on config name
    config_name = os.path.splitext(os.path.basename("config_files/config.toml"))[0]
    result_folder = f"results/{config_name}"
    os.makedirs(result_folder, exist_ok=True)

    # Load configuration
    config = load_config("config_files/config.toml")

    # Call the main function with config and result folder
    main(config, result_folder)
