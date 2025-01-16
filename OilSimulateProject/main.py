import time
import tomllib
from src.io.mesh_reader import Mesh
from src.simulation.simulator import Simulation

def load_config(filename):
    with open(filename, 'rb') as f:
        config = tomllib.load(f)
    return config

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
    print("No write frequency specified, skipping video output.")
else:
    print(f"Write frequency: {write_frequency}")

def main():
    start_time = time.time()
    
    file_path = f"data/mesh/{mesh_name}"

    # Create the mesh
    mesh = Mesh(file_path)

    oil_spill_simulation = Simulation(mesh, oil_spill_center, fishing_grounds, nSteps, tStart, tEnd, write_frequency)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\n\nExecution time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()
