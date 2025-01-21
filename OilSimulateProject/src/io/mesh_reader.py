import meshio
from ..cell.base_cell import CellFactory
import logging

# Configure logging for this module
logger = logging.getLogger(__name__)

class Mesh:
    """
    Represents a computational mesh loaded from a file. 

    Attributes:
        _file_name (str): Path to the mesh file.
        _points (list[Point]): List of 2D points in the mesh.
        _cells (list): List of cells in the mesh, created using the CellFactory.
    """

    def __init__(self, file_name: str):
        """
        Initializes the Mesh object by reading points and cells from the file.

        Args:
            file_name (str): Path to the mesh file.
        """
        self._file_name = file_name
        logger.info(f"Reading mesh from: {file_name}")
        msh = meshio.read(file_name)

        # Read points from the mesh file (assuming 2D points only)
        self._points = [Point(*point[:2]) for point in msh.points]

        # Read cells and create corresponding cell objects
        self._cells = []
        create_cell = CellFactory()
        index = 0

        for block in msh.cells:
            if block.type in ("line", "triangle"):
                for cell_points in block.data:
                    cell_obj = create_cell(cell_points, block.type, index, self)
                    self._cells.append(cell_obj)
                    index += 1
            else:
                # Skipping unsupported cell types (e.g., higher-dimensional cells)
                logger.debug(f"Skipping unsupported cell type: {block.type}")

        # Establish relationships and compute additional properties
        self.find_neighbours_and_edges()
        self.find_outward_normals()

    def find_neighbours_and_edges(self) -> None:
        """
        Computes and stores the neighbors and edges for each cell in the mesh.
        """
        total_cells = len(self._cells)
        print_interval = max(1, total_cells // 100)  # Update progress every 1%
        print(f"Storing neighbors for each cell in {self._file_name}:")

        for i, cell in enumerate(self._cells):
            cell.store_neighbours_and_edges()

            # Print progress at regular intervals
            if i % print_interval == 0 or i == total_cells - 1:
                progress = (i + 1) / total_cells * 100
                print(f"Progress: {progress:.2f}% ({i + 1}/{total_cells})", end='\r')

        print("\nNeighbor storage complete.\n")

    def find_outward_normals(self) -> None:
        """
        Computes and stores outward normals for all cells in the mesh.
        """
        for cell in self._cells:
            cell.store_outward_normals()

        print(f"Outward normals computed for {self._file_name}")

    @property
    def cells(self) -> list:
        """
        Returns the list of cells in the mesh.

        Returns:
            list: List of cell objects.
        """
        return self._cells

    @property
    def points(self) -> list:
        """
        Returns the list of points in the mesh.

        Returns:
            list: List of Point objects.
        """
        return self._points

class Point:
    """
    Represents a 2D point with x and y coordinates.

    Attributes:
        _x (float): The x-coordinate of the point.
        _y (float): The y-coordinate of the point.
    """

    def __init__(self, x: float, y: float):
        """
        Initializes a Point object with x and y coordinates.

        Args:
            x (float): X-coordinate.
            y (float): Y-coordinate.
        """
        self._x = x
        self._y = y

    @property
    def x(self) -> float:
        """
        Returns the x-coordinate of the point.

        Returns:
            float: X-coordinate.
        """
        return self._x

    @property
    def y(self) -> float:
        """
        Returns the y-coordinate of the point.

        Returns:
            float: Y-coordinate.
        """
        return self._y
