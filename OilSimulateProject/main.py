import time
import tomllib
import logging
from src.io.mesh_reader import Mesh
from src.simulation.simulator import Simulation
from src.io.config_reader import ConfigReader

# Set up logging to a file
log_filename = 'logfile.log'
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,  # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    handlers=[
        logging.FileHandler(log_filename),  # Log to file
        logging.StreamHandler()  # Optionally log to console (if you still want to see critical logs in the terminal)
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

# Load configuration
config = load_config("config_files/config.toml")

# Accessing settings
nSteps = config['settings']['nSteps']
tStart = config['settings']['tStart']
tEnd = config['settings']['tEnd']

# Accessing geometry
mesh_name = config['geometry']['meshName']
oil_spill_center = config['geometry']['oilSpillCenter']
fishing_grounds = config['geometry']['borders']
log_name = config['geometry']['logName']

write_frequency = config["IO"].get("writeFrequency", None)  # Default to None if not provided

if write_frequency is None:
    logger.warning("No write frequency specified, skipping video output.")
else:
    logger.info(f"Write frequency: {write_frequency}")

def main():
    start_time = time.time()
    logger.info("Starting the simulation...")

    file_path = f"data/mesh/{mesh_name}"

    try:
        # Create the mesh
        mesh = Mesh(file_path)
        logger.info(f"Mesh loaded successfully from {file_path}")
        
        # Create the simulation
        oil_spill_simulation = Simulation(mesh, oil_spill_center, fishing_grounds, nSteps, tStart, tEnd, write_frequency)
        logger.info("Simulation created successfully.")
        
    except Exception as e:
        logger.error(f"Error occurred during simulation setup: {e}")
        return

    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"Execution time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()