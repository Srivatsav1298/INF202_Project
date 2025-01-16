import time
import tomllib
from src.io.mesh_reader import Mesh, Point
from src.simulation.simulator import Simulation

def load_config(file_path):
    with open(file_path, 'rb') as f:  # Use 'r' if using the `toml` library
        config = tomllib.load(f)  # Replace with `toml.load(f)` if using `toml`
    return config

oil_spill_center = Point(0.35, 0.45)
fishing_grounds = ((0.0, 0.45), (0.0, 0.2))
nSteps = 240 # number of simulation steps from t = 0 to tEnd
tStart = 0 # start time of gif
tEnd = 0.5 # end time of gif and simulation
fps = round(nSteps / 8*((tEnd-tStart)/tEnd)) # this formula gives an ideal speed for the gif

def main():
    start_time = time.time()
    
    file_name = "data/mesh/bay.msh"
    
    # Create the mesh
    bay_mesh = Mesh(file_name)

    oil_spill_simulation = Simulation(bay_mesh, oil_spill_center, fishing_grounds, nSteps, tStart, tEnd, fps)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\nExecution time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()
