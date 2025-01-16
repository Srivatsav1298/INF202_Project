from abc import ABC, abstractmethod

class Cell(ABC):
    def __init__(self, index, points=None, mesh=None, neighbours=None):
        self._index = index
        self._points = points if points is not None else []
        self._mesh = mesh if mesh is not None else ""
        self._neighbours = neighbours if neighbours is not None else []
        self._oil_amount = None
        self._edge_vectors = []
        self._edge_points = []

    @abstractmethod
    def calculate_midpoint(self):
        pass

    @abstractmethod
    def store_neighbours_and_edges(self):
        pass

    @abstractmethod
    def store_outward_normals(self):
        pass

    @abstractmethod
    def is_boundary(self):
        pass
    
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
        
    @abstractmethod
    def __str__(self):
        pass

class CellFactory:
    def __init__(self):
        from .line_cell import Line
        from .triangle_cell import Triangle
        self._cell_types = {
            "line": Line,
            "triangle": Triangle
        }

    def __call__(self, cell, cell_type, index, mesh):
        if cell_type not in self._cell_types:
            raise ValueError(f"Unknown cell type: {cell_type}. Supported types are: {list(self._cell_types.keys())}")
        return self._cell_types[cell_type](index, cell, mesh)