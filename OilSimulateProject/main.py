import time
import argparse
import glob
import os
from src.io.mesh_reader import Mesh
from src.simulation.simulator import Simulation
from src.io.config_reader import ConfigReader

def parse_arguments():
    parser = argparse.ArgumentParser(description="Run oil spill simulations.")
    parser.add_argument("-c", "--config", type=str, help="Specify a single config file.")
    parser.add_argument("-f", "--folder", type=str, help="Specify a folder containing config files.")
    parser.add_argument("--find_all", action="store_true", help="Find all config files in the current folder.")
    return parser.parse_args()

def create_unique_folder(base_name):
    folder_name = base_name
    count = 1
    while os.path.exists(folder_name):
        folder_name = f"{base_name}_{count}"
        count += 1
    os.makedirs(folder_name)
    return folder_name

def load_config_files(args):
    config_files = []
    if args.config:
        if os.path.exists(args.config):
            config_files.append(args.config)
        else:
            print(f"Config file '{args.config}' not found.")
    elif args.folder:
        config_files = glob.glob(os.path.join(args.folder, "*.toml"))
        if not config_files:
            print(f"No config files found in folder '{args.folder}'.")
    elif args.find_all:
        config_files = glob.glob("*.toml")
        if not config_files:
            print("No config files found in the current folder.")
    return config_files

def main():
    # Parse command-line arguments
    args = parse_arguments()
    config_files = load_config_files(args)
    
    if not config_files:
        print("No valid configuration files found. Exiting.")
        return

    # Iterate through each config file
    for config_file in config_files:
        print(f"\nRunning simulation with config: {config_file}")
        
        try:
            # Load configuration
            config = ConfigReader(config_file).parameters
            
            # Extract parameters with defaults
            oil_spill_center = tuple(config.get("oil_spill_center", [0.35, 0.45]))
            nSteps = config.get("nSteps", 100)
            tStart = config.get("tStart", 0)
            tEnd = config.get("tEnd", 0.5)
            fps = config.get("fps", max(round(nSteps / 8), 1))
            write_frequency = config.get("writeFrequency", 10)
            restart_file = config.get("restartFile", None)
            if restart_file and not os.path.exists(restart_file):
                print(f"Warning: Restart file '{restart_file}' not found. Starting simulation from scratch.")
                restart_file = None

            # Create a unique output folder for this simulation run
            output_folder = create_unique_folder(f"output_{os.path.basename(config_file).split('.')[0]}")
            print(f"Results will be saved in: {output_folder}")

            # Start timing
            start_time = time.time()

            # Create and setup the mesh
            file_name = "data/mesh/bay.msh"
            bay_mesh = Mesh(file_name)

            # Build neighbour relationships for each cell and related outward normal
            bay_mesh.find_neighbours()
            bay_mesh.find_outward_normals()

            # Initialize the simulation
            oil_spill_simulation = Simulation(
                bay_mesh,
                oil_spill_center,
                nSteps,
                tStart,
                tEnd,
                fps,
                write_frequency,
                restart_file
            )
            oil_spill_simulation.initialize_oil_spill()
            oil_spill_simulation.oil_movement()

            # Log execution time
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Execution time: {elapsed_time:.2f} seconds")

        except Exception as e:
            print(f"Error while processing config '{config_file}': {e}")

if __name__ == "__main__":
    main()
