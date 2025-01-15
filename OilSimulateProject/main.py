import time
from src.io.mesh_reader import Mesh, Point
from src.simulation.simulator import Simulation

oil_spill_center = Point(0.35, 0.45)
nSteps = 240 # number of simulation steps
tStart = 0
tEnd = 0.5
fps = round(nSteps / 8*((tEnd-tStart)/tEnd)) # this formula gives an ideal speed for the gif

def main():
    start_time = time.time()
    
    file_name = "data/mesh/bay.msh"
    
    # Create the mesh
    bay_mesh = Mesh(file_name)

    oil_spill_simulation = Simulation(bay_mesh, oil_spill_center, nSteps, tStart, tEnd, fps)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\nExecution time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()
