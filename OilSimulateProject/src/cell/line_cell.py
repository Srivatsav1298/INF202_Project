from .base_cell import Cell
import logging

logger = logging.getLogger(__name__)

class Line(Cell):
    """
    Represents a line cell in the computational mesh.

    Attributes:
        _oil_amount: The amount of oil contained in the cell.
        _midpoint: The geometric midpoint of the line.
        _velocity_field: The velocity field at the cell's midpoint.
    """

    def __init__(self, index: int, points: list[int], mesh):
        """
        Initialize a Line instance.

        Args:
            index: Unique identifier for the line cell.
            points: Indices of points defining the line.
            mesh: The mesh this line cell belongs to.
        """
        super().__init__(index, points, mesh)
        self._oil_amount = 0 # Line cells should always have 0 oil amount
        self._midpoint = self.calculate_midpoint()
        self._velocity_field = self.calculate_velocity_field()

    def store_neighbours_and_edges(self):
        """
        Populate the neighbours list for the cell based on shared points with other cells.

        Compares the line cell with all other cells in the mesh to determine if they share
        the required number of points to qualify as neighbours.
        """
        self_set = set(self._points)
        for cell in self._mesh.cells:
            point_set = set(cell.points)
            matching_points = point_set.intersection(self_set)
            if isinstance(self, Line) and isinstance(cell, Line):
                # Two line cells are neighbours if they share exactly one point
                if len(matching_points) == 1:
                    self._neighbours.append(cell)
            else:
                # Other cell types require two shared points to qualify as neighbours
                if len(matching_points) == 2:
                    self._neighbours.append(cell)

    def store_outward_normals(self):
        """
        The simulation does not require outward normals for Line cells.
        """
        pass

    def calculate_midpoint(self) -> tuple[float, float]:
        """
        Calculate and store the geometric midpoint of the line.

        Returns:
            tuple[float, float]: Coordinates of the midpoint.
        """
        point_coordinates = [self._mesh.points[i] for i in self._points]
        x = sum(p.x for p in point_coordinates) / 2
        y = sum(p.y for p in point_coordinates) / 2
        self._midpoint = (x, y)
        return self._midpoint
    
    def calculate_velocity_field(self) -> tuple[float, float]:
        """
        Calculate the velocity field for the cell based on its midpoint.

        Returns:
            tuple[float, float]: Velocity field vector at the midpoint.
        """
        x = self._midpoint[0]
        y = self._midpoint[1]
        self._velocity_field = (y - (0.2*x), -x)
        return self._velocity_field
    
    def is_boundary(self) -> bool:
        """
        Determine if the line cell is a boundary cell.

        Returns:
            bool: True for all line cells
        """
        return True  
    
    @property
    def midpoint(self) -> tuple[float, float]:
        """Get the midpoint of the line."""
        return self._midpoint
    
    @property
    def velocity_field(self) -> tuple[float, float]:
        """Get the velocity field of the line."""
        return self._velocity_field
    
    @property
    def oil_amount(self) -> float:
        """Get the amount of oil contained in the cell."""
        return self._oil_amount
    
    @oil_amount.setter
    def oil_amount(self, value: float):
        """
        Set the amount of oil in the line.

        Args:
            value (float): The new oil amount. Must be non-negative.

        Raises:
            ValueError: If the value is negative.
        """
        if value < 0:
            raise ValueError("Oil amount cannot be negative.")
        self._oil_amount = value

    def __str__(self) -> str:
        """
        Return a string representation of the line cell.

        Returns:
            str: Description of the line including index, boundary status, and neighbours.
        """
        neighbour_indices = [n.index for n in self._neighbours]
        return f"Line(index={self._index}, boundary={self.is_boundary()}, neighbours={neighbour_indices})"