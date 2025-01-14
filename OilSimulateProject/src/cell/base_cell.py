from abc import ABC, abstractmethod

class Cell(ABC):
    def __init__(self, index, points=None, mesh=None, neighbours=None):
        self._index = index
        self._points = points if points is not None else []
        self._mesh = mesh if mesh is not None else ""
        self._neighbours = neighbours if neighbours is not None else []
        self._midpoint = None
        self._oil_amount = None
        self._edge_vectors = []
        self._edge_points = []

    @property
    def index(self):
        return self._index

    @property
    def neighbours(self):
        return self._neighbours

    @property
    def points(self):
        return self._points
    
    @property
    def oil_amount(self):
        return self._oil_amount
    
    @property
    def edge_vectors(self):
        return self._edge_vectors

    def store_neighbours(self):
        from .line_cell import Line

        self_set = set(self._points)
        for cell in self._mesh.cells:
            point_set = set(cell.points)
            matching_points = point_set.intersection(self_set)
            point_coordinates = [self._mesh.points[i] for i in matching_points]
            if isinstance(self, Line) and isinstance(cell, Line):
                # When comparing a line to another line, they only need 1 point in common
                if len(matching_points) == 1:
                    self._neighbours.append(cell)
            else:
                # Every other comparison needs 2 points in common
                if len(matching_points) == 2:
                    self._neighbours.append(cell)
                    self._edge_vectors.append([
                    point_coordinates[0].x - point_coordinates[1].x,
                    point_coordinates[0].y - point_coordinates[1].y])
                    self._edge_points.append(point_coordinates)

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

    @property
    def x(self):
        return self._x

    @property
    def y(self):
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