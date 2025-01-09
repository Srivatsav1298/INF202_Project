from .base_cell import Cell, Point
import math

class Triangle(Cell):
    def __init__(self, index, points=None, mesh=None, neighbours=None):
        super().__init__(index, points, mesh, neighbours)
        self._midpoint = None
        self._area = None
        self._velocityfield = None
        self._oil_intensity = None

    def calculate_midpoint(self):
        point_coordinates = [self._mesh.get_points()[i] for i in self._points]
        x = sum(p.get_x() for p in point_coordinates) / 3
        y = sum(p.get_y() for p in point_coordinates) / 3
        self._midpoint = Point(x, y)
        return self._midpoint
    
    def initial_oil_intensity(self):
        oil_center = (0.35, 0.45)
        midpoint = self.calculate_midpoint()
        self._oil_intensity = math.exp(- ((midpoint.get_x() - oil_center[0])**2 + (midpoint.get_y() - oil_center[1])**2) / (0.01))
        return self._oil_intensity

    def calculate_area(self):
        point_coordinates = [self._mesh.get_points()[i] for i in self._points]
        x1, y1 = point_coordinates[0]._x, point_coordinates[0]._y
        x2, y2 = point_coordinates[1]._x, point_coordinates[1]._y
        x3, y3 = point_coordinates[2]._x, point_coordinates[2]._y

        self._area = 0.5 * abs(
            x1*(y2-y3) + x2*(y3-y1) + x3*(y1-y2)
        )
        return self._area

    def __str__(self):
        neighbour_indices = [n.get_index() for n in self._neighbours]
        midpoint = self.calculate_midpoint()
        return (
    f"Triangle(index={self._index}, "
    f"boundary={self.is_boundary()}, "
    f"neighbours={neighbour_indices}, "
    f"area={self.calculate_area():.4g}, "
    f"midpoint=({midpoint._x:.4g}, {midpoint._y:.4g}))"
)