import os

def write_solution(mesh, folder="default", i=0):
    """
    Write the oil value of each cell in the mesh to a .txt file.
    
    :param folder: Subfolder under 'solutions/' to store the file.
    :param i: Index or identifier for the solution file.
    """

    # 1. Make sure the output directory exists
    #output_dir = os.path.join("solutions", folder)
    output_dir = "solutions"
    os.makedirs(output_dir, exist_ok=True)
    
    # 3. Collect oil values for each cell
    lines = []
    for cell_index, cell in enumerate(mesh.cells):
        # Example: assume each cell has an attribute 'oil_value'
        oil_value = cell.oil_amount  
        # Add it to our list of lines. 
        # Here we format each line as "Cell X: oil_value"
        lines.append(f"Cell {cell_index}: {oil_value}\n")
    
    # 4. Write all lines to the solution file
    solution_file = os.path.join(output_dir, f"solution{i}.txt")
    with open(solution_file, "w") as file:
        file.writelines(lines)
    
    print(f"Oil values written to {solution_file}")
