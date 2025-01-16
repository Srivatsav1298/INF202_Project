import time
import tomllib
from src.io.mesh_reader import Mesh
from src.simulation.simulator import Simulation

def load_config(filename):
    with open(filename, 'rb') as f:  # Use 'r' if using the `toml` library
        config = tomllib.load(f)  # Replace with `toml.load(f)` if using `toml`
    return config

config = load_config("config/config.toml")  # Path to your TOML file

# Accessing settings
nSteps = config['settings']['nSteps']
tStart = config['settings']['tStart']
tEnd = config['settings']['tEnd']

# Accessing geometry
mesh_name = config['geometry']['meshName']
oil_spill_center = config['geometry']['oilSpillCenter']
fishing_grounds = config['geometry']['borders']
log_name = config['geometry']['logName']

fps = config['IO']['writeFrequency']

def main():
    start_time = time.time()
    
    file_path = f"data/mesh/{mesh_name}"

    # Create the mesh
    mesh = Mesh(file_path)

    oil_spill_simulation = Simulation(mesh, oil_spill_center, fishing_grounds, nSteps, tStart, tEnd, fps)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\nExecution time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()
