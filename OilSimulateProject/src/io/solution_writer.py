import os

def write_solution(mesh, time_val: float, total_oil: float, config_name: str):
    """
    Writes the oil value of each cell in the mesh to a .txt file in the 'solutions' directory.

    Args:
        mesh: The computational mesh containing cells as objects with an 'oil_amount' attribute.
        time_val (float): The current simulation time.
        total_oil (float): Total amount of oil in the fishing grounds at the current time step.
        config_name (str): Name used to identify the output file.

    Creates:
        A text file in the 'solutions' directory with the oil values for each cell in the mesh.
    """

    output_dir = "solutions"
    os.makedirs(output_dir, exist_ok=True) # Ensure the directory exists
    
    lines = []

    # Prepare the header line with time and total oil information
    lines.append(f"t = {time_val}, total_oil_in_fishing_grounds = {total_oil}\n")

    # Add the oil values for each cell
    for cell_index, cell in enumerate(mesh.cells):
        oil_value = cell.oil_amount  
        lines.append(f"Cell {cell_index}: {oil_value}\n")
    
    # Define the output file path
    solution_file = os.path.join(output_dir, f"{config_name}_solution.txt")

    # Write the lines to the file
    with open(solution_file, "w") as file:
        file.writelines(lines)
    
    print(f"Oil values successfully written to {solution_file}")