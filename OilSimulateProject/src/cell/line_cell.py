from .base_cell import Cell, Point

class Line(Cell):
    def __init__(self, index, points=None, mesh=None, neighbours=None):
        super().__init__(index, points, mesh, neighbours)
        self._oil_amount = 0

    def calculate_midpoint(self):
        point_coordinates = [self._mesh.points[i] for i in self._points]
        x = sum(p.x for p in point_coordinates) / 2
        y = sum(p.y for p in point_coordinates) / 2
        self._midpoint = Point(x, y)
        return self._midpoint

    def __str__(self):
        neighbour_indices = [n.index for n in self._neighbours]
        return f"Line(index={self._index}, boundary={self.is_boundary()}, neighbours={neighbour_indices})"