import time
from src.io.mesh_reader import Mesh  # or from oilsimulateproject.src.io.mesh_reader import Mesh

def main():
    start_time = time.time()  # Start the timer
    
    # Replace with an actual mesh file name that you have
    file_name = "data/mesh/bay.msh"
    
    # Create the mesh
    mesh = Mesh(file_name)

    # Build neighbour relationships
    mesh.find_neighbours()

    # Print out each cell
    for cell in mesh.get_cells():
        print(cell)

    end_time = time.time()  # End the timer
    elapsed_time = end_time - start_time
    print(f"\nExecution time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()
