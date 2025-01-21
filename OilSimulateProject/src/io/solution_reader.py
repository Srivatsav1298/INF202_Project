def initialize_oil_spill(mesh, solution_file):
    """
    Initializes the oil distribution on the computational mesh by reading oil amounts
    from a solution file and assigning them to the corresponding cells.

    Args:
        mesh: The computational mesh containing cells as objects with an 'oil_amount' attribute.
        solution_file (str): Path to the file containing oil distribution data.

    Raises:
        FileNotFoundError: If the solution file cannot be found.
        ValueError: If the file contains invalid or improperly formatted data.
    """
    # Open and read the file
    with open(solution_file, "r") as file:
        lines = file.readlines()

    cell_oil_values = {}

    # Process each line
    for line in lines:
        line = line.strip()  # Remove leading and trailing whitespace
        if line.startswith("t ="):
            # Ignore the first line
            continue
        elif line.startswith("Cell"):
            # Extract cell ID and oil amount
            cell_parts = line.split(":")
            cell_id = int(cell_parts[0].split()[1])
            oil_amount = float(cell_parts[1].strip())
            cell_oil_values[cell_id] = oil_amount

    # Assign oil amounts to the mesh cells        
    for i, cell in enumerate(mesh.cells):
        # Use oil amount from file if available, otherwise default to 0.0
        cell.oil_amount = cell_oil_values.get(i, 0.0)