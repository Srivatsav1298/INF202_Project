import time
from src.io.mesh_reader import Mesh

def main():
    start_time = time.time()  # Start the timer
    
    file_name = "data/mesh/bay.msh"
    
    # Create the mesh
    bay_mesh = Mesh(file_name)

    # Build neighbour relationships
    bay_mesh.find_neighbours()

    # Print out each cell
    for cell in bay_mesh.cells:
        print(cell)

    end_time = time.time()  # End the timer
    elapsed_time = end_time - start_time
    print(f"\nExecution time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()
