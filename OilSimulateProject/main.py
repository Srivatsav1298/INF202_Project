import time
from src.io.mesh_reader import Mesh
from src.simulation.simulator import Simulation

def main():
    start_time = time.time()  # Start the timer
    
    file_name = "data/mesh/bay.msh"
    
    # Create the mesh
    bay_mesh = Mesh(file_name)

    # Build neighbour relationships
    bay_mesh.find_neighbours()
    bay_mesh.find_outward_normals()

    oil_spill_simulation = Simulation(bay_mesh, (0.35, 0.45))
    oil_spill_simulation.initialize_oil_spill()
    oil_spill_simulation.oil_movement()

    end_time = time.time()  # End the timer
    elapsed_time = end_time - start_time
    print(f"\nExecution time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()
