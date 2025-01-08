"""
The problem
The fishing town of “Bay City” has reported an oil spill from one of their ships. They have enlisted
your help to assess the impact of the spill on their fishing grounds and to determine the necessary
measures to protect the fish population. Meanwhile, another group of researchers is modeling oceanic
flows. To test your code, they have provided a simplified flow field that approximates the main currents
in this region. Additionally, you are supplied with a two-dimensional map of “Bay City,” including
the coastline and surrounding ocean, along with a corresponding computational mesh, “bay.msh”. To
determine positions on this map, we use the coordinate axes x and y, where the point (0, 0) is located
at the lower bottom of the map. Currently, the oil distrubution is centered around teh spatial point
xvector_* = (x_*, y_*) = (0.35, 0.45) 

The fishing grounds are located in the area [0.0, 0.45] x [0.0, 0.2], that is the x-coordinate lies in
the interval [0.0, 0.2]. The movement of oil is dictated by the underlying flow field which takes the form
v(xvector)= ((y - 0.2x), (-x))
"""

import meshio
from abc import ABC, abstractmethod

class CellFactory:
    def __init__(self):
        self._cell_types = {"line": Line, "triangle": Triangle}

    def __call__(self, cell, cell_type, index, mesh):
        return self._cell_types[cell_type](index, cell, mesh)

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
        self_set = set(self._points)
        for cell in self._mesh.get_cells():
            point_set = set(cell.get_points())
            if isinstance(self, Line) and isinstance(cell, Line):
                # When comparing a line to another line, they only need 1 point in common 
                if len(point_set.intersection(self_set)) == 1: 
                    self._neighbours.append(cell)
            else:
                # every other comparison needs 2 points in common                                              
                if len(point_set.intersection(self_set)) == 2:
                    self._neighbours.append(cell)

    def is_boundary(self):
        if isinstance(self, Line):
            return True  # All Line cells are boundary cells
        if isinstance(self, Triangle):
            # A Triangle is a boundary cell if any of its neighbors is a Line
            return any(isinstance(neighbor, Line) for neighbor in self._neighbours)
        return False
    
    @abstractmethod
    def __str__(self):
        pass

class Line(Cell):
    def __init__(self, index, points=None, mesh=None, neighbours=None):
        super().__init__(index, points, mesh, neighbours)

    def __str__(self):
        neighbour_indices = [neighbour.get_index() for neighbour in self._neighbours]
        return f"Line(index={self._index}, boundary={self.is_boundary()}, neighbours={neighbour_indices})"

class Triangle(Cell):
    def __init__(self, index, points=None, mesh=None, neighbours=None):
        super().__init__(index, points, mesh, neighbours)
        self._midpoint = None
        self._area = None
        self._velocityfield = None

    def calculate_midpoint(self):
        # Use the indices in self._points to look up the actual points in the mesh
        point_coordinates = [self._mesh.get_points()[i] for i in self._points]
        x = sum(point._x for point in point_coordinates) / 3
        y = sum(point._y for point in point_coordinates) / 3
        self._midpoint = Point(x, y)
        return self._midpoint

    def calculate_area(self):
        # Use the indices in self._points to look up the actual points in the mesh
        point_coordinates = [self._mesh.get_points()[i] for i in self._points]
        x1, y1 = point_coordinates[0]._x, point_coordinates[0]._y
        x2, y2 = point_coordinates[1]._x, point_coordinates[1]._y
        x3, y3 = point_coordinates[2]._x, point_coordinates[1]._y

        self._area = 0.5 * abs(x1*(y2-y3)+x2*(y3-y1)+x3(y1-y2))
        

    def __str__(self):
        neighbour_indices = [neighbour.get_index() for neighbour in self._neighbours]
        return f"Triangle(index={self._index}, boundary={self.is_boundary()}, neighbours={neighbour_indices})"

class Point:
    def __init__(self, x, y):
        self._x = x
        self._y = y

class Mesh:
    def __init__(self, file_name):
        msh = meshio.read(file_name)
        
        # Read points from the mesh file (assumes 2D points)
        self._points = [Point(*point[:2]) for point in msh.points]
        
        # Read cells and create cell objects
        self._cells = []
        create_cell = CellFactory()
        index = 0
        for cell_type in msh.cells:
            if cell_type.type in ("line", "triangle"):
                for cell in cell_type.data:
                    tmp = create_cell(cell, cell_type.type, index, self)
                    self._cells.append(tmp)
                    index += 1
            else:
                pass
        
    def get_cells(self):
        return self._cells
    
    def get_points(self):
        return self._points
    
    def find_neighbours(self):
        for cell in self._cells:
            cell.store_neighbours()

bay_mesh = Mesh("OilSimulateProject/data/mesh/bay.msh")

# bay_mesh.find_neighbours()

cell = bay_mesh.get_cells()[2000]
print(cell.calculate_midpoint())

