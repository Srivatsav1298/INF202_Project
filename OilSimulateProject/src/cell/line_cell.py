from .base_cell import Cell

class Line(Cell):
    def __init__(self, index, points=None, mesh=None, neighbours=None):
        super().__init__(index, points, mesh, neighbours)
        self._oil_amount = 0
        self._midpoint = self.calculate_midpoint()

    def store_neighbours_and_edges(self):
        self_set = set(self._points)
        for cell in self._mesh.cells:
            point_set = set(cell.points)
            matching_points = point_set.intersection(self_set)
            if isinstance(self, Line) and isinstance(cell, Line):
                # When comparing a line to another line, they only need 1 point in common
                if len(matching_points) == 1:
                    self._neighbours.append(cell)
            else:
                # Every other comparison needs 2 points in common
                if len(matching_points) == 2:
                    self._neighbours.append(cell)

    def store_outward_normals(self):
        pass

    def calculate_midpoint(self):
        from ..io.mesh_reader import Point
        point_coordinates = [self._mesh.points[i] for i in self._points]
        x = sum(p.x for p in point_coordinates) / 2
        y = sum(p.y for p in point_coordinates) / 2
        self._midpoint = Point(x, y)
        return self._midpoint
    
    @property
    def midpoint(self):
        return self._midpoint

    def __str__(self):
        neighbour_indices = [n.index for n in self._neighbours]
        return f"Line(index={self._index}, boundary={self.is_boundary()}, neighbours={neighbour_indices})"