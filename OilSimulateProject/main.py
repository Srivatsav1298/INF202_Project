import time
from src.io.mesh_reader import Mesh
from src.simulation.simulator import Simulation

oil_spill_center = (0.35, 0.45)
nSteps = 100
tStart = 0
tEnd = 0.5
fps = round(nSteps/8)

def main():
    start_time = time.time()
    
    # Create and setup the mesh
    file_name = "data/mesh/bay.msh"
    bay_mesh = Mesh(file_name)

    # Build neighbour relationships for each cell and related outward normal
    bay_mesh.find_neighbours()
    bay_mesh.find_outward_normals()

    oil_spill_simulation = Simulation(bay_mesh, oil_spill_center, nSteps, tStart, tEnd, fps)
    oil_spill_simulation.initialize_oil_spill()
    oil_spill_simulation.oil_movement()

    end_time = time.time()  # End the timer
    elapsed_time = end_time - start_time
    print(f"\nExecution time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()