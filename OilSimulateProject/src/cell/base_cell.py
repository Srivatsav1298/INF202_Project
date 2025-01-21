from abc import ABC, abstractmethod

class Cell(ABC):
    """
    Abstract base class for different types of cells in a computational mesh.

    Attributes:
        index: Unique identifier for the cell.
        points: Coordinates of the points defining the cell.
        mesh: Name or reference to the mesh this cell belongs to.
        neighbours: List of indices of neighboring cells.
        oil_amount: Amount of oil contained within the cell (if applicable).
        edge_vectors: Vectors representing the cell's edges.
        edge_points: Points representing the start and end of each edge.
    """
    def __init__(self, index: int, points: list[int], mesh):
        self._index = index
        self._points = points
        self._mesh = mesh
        self._neighbours = []
        self._oil_amount = 0 # Placeholder for oil amount, will be adjusted later if needed.
        self._edge_vectors = [] # Will store edge vectors of the cell.
        self._edge_points = []  # Will store start and end points of edges.

    @abstractmethod
    def calculate_midpoint(self):
        """
        Calculate the geometric midpoint of the cell.

        Returns:
            tuple: Coordinates of the midpoint.
        """
        pass

    @abstractmethod
    def calculate_velocity_field(self):
        """
        Calculate the velocity field for the cell based on physical parameters.
        """
        pass

    @abstractmethod
    def store_neighbours_and_edges(self):
        """
        Populate the neighbours and edge information for the cell.
        """
        pass

    @abstractmethod
    def store_outward_normals(self):
        """
        Calculate and store outward-facing normal vectors for each edge of the cell.
        """
        pass

    @abstractmethod
    def is_boundary(self):
        """
        Determine if the cell is a boundary cell.

        Returns:
            bool: True if the cell is a boundary cell, False otherwise.
        """
        pass
    
    @property
    def index(self):
        """Get the index of the cell."""
        return self._index

    @property
    def neighbours(self):
        """Get the list of neighbouring cell indices."""
        return self._neighbours

    @property
    def points(self):
        """Get the coordinates of the cell's points."""
        return self._points
    
    @property
    def oil_amount(self):
        """Get the amount of oil contained in the cell."""
        return self._oil_amount
    
    @property
    def edge_vectors(self):
        """Get the edge vectors of the cell."""
        return self._edge_vectors
        
    @abstractmethod
    def __str__(self):
        """
        Return a string representation of the cell.

        Returns:
            str: String description of the cell.
        """
        pass

class CellFactory:
    """
    Factory class to create instances of different types of cells.

    Attributes:
        _cell_types (Dict[str, Type[Cell]]): Mapping of cell type names to their classes.
    """
    def __init__(self):
        # Importing specific cell types to ensure modularity and avoid circular imports.
        from .line_cell import Line
        from .triangle_cell import Triangle
        self._cell_types = {
            "line": Line,
            "triangle": Triangle
        }

    def __call__(self, cell: list, cell_type: str, index: int, mesh):
        """
        Create a cell of the specified type.

        Args:
            cell: Points defining the cell.
            cell_type: The type of the cell (e.g., "line", "triangle").
            index: Unique identifier for the cell.
            mesh: The mesh to which this cell belongs.

        Returns:
            Cell: An instance of the specified cell type.

        Raises:
            ValueError: If an unsupported cell type is requested.
        """
        if cell_type not in self._cell_types:
            raise ValueError(f"Unknown cell type: {cell_type}. Supported types are: {list(self._cell_types.keys())}")
        return self._cell_types[cell_type](index, cell, mesh)