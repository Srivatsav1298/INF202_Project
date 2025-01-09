from .base_cell import Cell, Point

class Triangle(Cell):
    def __init__(self, index, points=None, mesh=None, neighbours=None):
        super().__init__(index, points, mesh, neighbours)
        self._midpoint = None
        self._area = None
        self._velocityfield = None

    def calculate_midpoint(self):
        point_coordinates = [self._mesh.get_points()[i] for i in self._points]
        x = sum(p._x for p in point_coordinates) / 3
        y = sum(p._y for p in point_coordinates) / 3
        self._midpoint = Point(x, y)
        return self._midpoint

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
        return (
    f"Triangle(index={self._index}, "
    f"boundary={self.is_boundary()}, "
    f"neighbours={neighbour_indices}, "
    f"area={self.calculate_area():.4g}, "
    f"midpoint={self.calculate_midpoint()})"
)