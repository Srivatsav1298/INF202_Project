from .base_cell import Cell
import math
import numpy as np

class Triangle(Cell):
    """
    Represents a Triangle cell in the computational mesh.

    Attributes:
        _mipoint: The geometric midpoint of the triangle.
        _area: The geomtric area of the triangle.
        _velocity_field: The velocity field at the cell's midpoint.
        _outward_normals: A list of outward normal vectors for each triangle edge.
    """
    def __init__(self, index: int, points: list[int], mesh):
        """
        Initialize a Triangle instance.

        Args:
            index: Unique identifier for the triangle cell.
            points: Indices of points defining the Triangle.
            mesh: The mesh this triangle cell belongs to.
        """
        super().__init__(index, points, mesh)
        self._midpoint = self.calculate_midpoint()
        self._area = self.calculate_area()
        self._velocity_field = self.calculate_velocity_field()
        self._outward_normals = []

    def store_neighbours_and_edges(self):
        """
        Populate the neighbours list for the cell based on shared points with other cells.

        Compares the Triangle cell with all other cells in the mesh to determine if they share
        the required number of points to qualify as neighbours.
        """
        self_set = set(self._points)
        for cell in self._mesh.cells:
            point_set = set(cell.points)
            matching_points = point_set.intersection(self_set)
            point_coordinates = [self._mesh.points[i] for i in matching_points]

            # Other cell type requires two shared points to be neighbour
            if len(matching_points) == 2:
                self._neighbours.append(cell)
                self._edge_vectors.append([
                point_coordinates[0].x - point_coordinates[1].x,
                point_coordinates[0].y - point_coordinates[1].y])
                self._edge_points.append(point_coordinates)    

    def calculate_midpoint(self) -> tuple[float, float]:
        """
        Calculate and store the geometric midpoint of the Triangle.

        Returns:
            tuple[float, float]: Coordinates of the midpoint.
        """
        point_coordinates = [self._mesh.points[i] for i in self._points]
        x = sum(p.x for p in point_coordinates) / 3
        y = sum(p.y for p in point_coordinates) / 3
        self._midpoint = (x, y)
        return self._midpoint

    def calculate_area(self) -> float:
        """
        Calculate the area for the cell based on its three points.

        Returns:
            float: 2D area of Triangle
        """
        point_coordinates = [self._mesh.points[i] for i in self._points]
        x1, y1 = point_coordinates[0].x, point_coordinates[0].y
        x2, y2 = point_coordinates[1].x, point_coordinates[1].y
        x3, y3 = point_coordinates[2].x, point_coordinates[2].y

        self._area = 0.5 * abs(
            (x1-x3)*(y2-y1) - (x1-x2)*(y3-y1)
        )
        
        return self._area
    
    def calculate_oil_amount(self, oil_spill_center: tuple[float, float]) -> float:
        """
        Calculates the oil amount in the cell based on gaussian function.
        The oil amount is determined based on the cell's distance from the center 
        of the oil spill.

        Args:
            oil_spill_center: The coordinates of the oil spill center 

        Returns:
            float: The calculated amount of oil in the cell.
        """
        midpoint = self._midpoint
        self._oil_amount = math.exp(- ((midpoint[0] - oil_spill_center[0])**2 + (midpoint[1] - oil_spill_center[1])**2) / (0.01))
        return self._oil_amount

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

    def store_outward_normals(self):
        """
        Calculate and store outward normal vectors for each triangle edge.
        """
        for i, edge in enumerate(self._edge_vectors):
            perp_vector = np.array([-edge[1], edge[0]])
            normal = perp_vector / np.linalg.norm(perp_vector)

            midpoint = np.array([self._midpoint[0], self._midpoint[1]])
            p = np.array([self._edge_points[i][0].x, self._edge_points[i][0].y])

            to_p = p - midpoint

            if np.dot(normal, to_p) < 0:
                normal = -normal

            self._outward_normals.append(normal)
    
    def update_oil_amount(self, oil_over_each_facet: list[float]):
        """
        Update the oil amount in the triangle by accounting for oil difference.

        Args:
            oil_over_each_facet: Oil amounts passed through each edge.
        """
        oil_difference = sum(oil_over_each_facet)
        new_oil_amount = self._oil_amount + oil_difference
        self._oil_amount = new_oil_amount

    def is_boundary(self) -> bool:
        """
        Check if the triangle is a boundary cell.

        Returns:
            bool: True if the triangle shares an edge with a Line cell.
        """
        from .line_cell import Line
        return any(isinstance(neighbor, Line) for neighbor in self._neighbours)
    
    @property
    def midpoint(self) -> float:
        """Get the midpoint of the triangle."""
        return self._midpoint

    @property
    def oil_amount(self) -> float:
        """Get the oil amount in the triangle."""
        return self._oil_amount
    
    @oil_amount.setter
    def oil_amount(self, value: float):
        """
        Set the oil amount in the triangle.

        Args:
            value (float): New oil amount. Must be non-negative.

        Raises:
            ValueError: If the value is negative.
        """
        if value < 0:
            raise ValueError("Oil amount cannot be negative.")
        self._oil_amount = value
    
    @property
    def outward_normals(self) -> list[np.ndarray]:
        """Get the outward normals of the triangle."""
        return self._outward_normals
    
    @property
    def velocity_field(self) -> tuple[float, float]:
        """Get the velocity field of the triangle."""
        return self._velocity_field

    @property
    def area(self) -> float:
        """Get the area of the triangle."""
        return self._area

    def __str__(self) -> str:
        """
        Return a string representation of the triangle cell.

        Returns:
            str: Description of the triangle, including index, area, and neighbours.
        """
        neighbour_indices = [n.index for n in self._neighbours]
        midpoint = self._midpoint
        return (
    f"Triangle(index={self._index}, "
    f"boundary={self.is_boundary()}, "
    f"neighbours={neighbour_indices}, "
    f"area={self.area:.4g}, "
    f"midpoint=({midpoint[0]:.4g}, {midpoint[1]:.4g}))"
)