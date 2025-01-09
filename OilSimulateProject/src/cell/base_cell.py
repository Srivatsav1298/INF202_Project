from abc import ABC, abstractmethod

class Cell(ABC):
    def __init__(self, index, points=None, mesh=None, neighbours=None):
        self._index = index
        self._points = points if points is not None else []
        self._mesh = mesh if mesh is not None else ""
        self._neighbours = neighbours if neighbours is not None else []

    def get_index(self):
        return self._index

    def get_neighbours(self):
        return self._neighbours

    def get_points(self):
        return self._points

    def store_neighbours(self):
        from .line_cell import Line
        from .triangle_cell import Triangle

        self_set = set(self._points)
        for cell in self._mesh.get_cells():
            point_set = set(cell.get_points())
            if isinstance(self, Line) and isinstance(cell, Line):
                # When comparing a line to another line, they only need 1 point in common
                if len(point_set.intersection(self_set)) == 1:
                    self._neighbours.append(cell)
            else:
                # Every other comparison needs 2 points in common
                if len(point_set.intersection(self_set)) == 2:
                    self._neighbours.append(cell)

    def is_boundary(self):
        from .line_cell import Line
        from .triangle_cell import Triangle

        if isinstance(self, Line):
            return True
        if isinstance(self, Triangle):
            return any(isinstance(neighbor, Line) for neighbor in self._neighbours)
        return False

    @abstractmethod
    def __str__(self):
        pass

class Point:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

class CellFactory:
    def __init__(self):
        from .line_cell import Line
        from .triangle_cell import Triangle
        self._cell_types = {
            "line": Line,
            "triangle": Triangle
        }

    def __call__(self, cell, cell_type, index, mesh):
        return self._cell_types[cell_type](index, cell, mesh)