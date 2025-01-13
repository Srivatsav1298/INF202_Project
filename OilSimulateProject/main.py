import time
from src.io.mesh_reader import Mesh
from src.visualization.plotter import plot_mesh, create_animation
from src.simulation.simulator import Simulation

def main():
    start_time = time.time()
    
    # Create and setup the mesh
    file_name = "data/mesh/bay.msh"
    bay_mesh = Mesh(file_name)
    bay_mesh.find_neighbours()
    
    # Create simulation
    oil_spill_simulation = Simulation(
        bay_mesh, 
        oil_spill_center=(0.35, 0.45),
        end_time=2.0,  # Simulate for 2 time units
        dt=0.01
    )
    
    # Initialize
    oil_spill_simulation.initialize_oil_spill()
    
    # Plot initial state
    print("Plotting initial state...")
    plot_mesh(bay_mesh)
    
    # Create and save animation
    print("Creating animation...")
    create_animation(oil_spill_simulation, num_frames=200)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\nExecution time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()