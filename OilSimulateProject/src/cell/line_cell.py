from .base_cell import Cell
import logging

logger = logging.getLogger(__name__)

class Line(Cell):
    def __init__(self, index, points=None, mesh=None, neighbours=None):
        logger.debug(f"Initializing Line cell with index {index}")
        super().__init__(index, points, mesh, neighbours)
        self._oil_amount = 0
        self._midpoint = self.calculate_midpoint()
        self._velocity_field = self.calculate_velocity_field()

    def store_neighbours_and_edges(self):
        logger.info(f"Storing neighbors for Line cell {self._index}")
        try:
            self_set = set(self._points)
            for cell in self._mesh.cells:
                point_set = set(cell.points)
                matching_points = point_set.intersection(self_set)
                if isinstance(self, Line) and isinstance(cell, Line):
                    if len(matching_points) == 1:
                        self._neighbours.append(cell)
                else:
                    if len(matching_points) == 2:
                        self._neighbours.append(cell)
        except Exception as e:
            logger.error(f"Error storing neighbors for Line cell {self._index}: {e}")
            raise

    def store_outward_normals(self):
        logger.debug(f"Storing outward normals for Line cell {self._index}")
        pass

    def calculate_midpoint(self):
        try:
            point_coordinates = [self._mesh.points[i] for i in self._points]
            x = sum(p.x for p in point_coordinates) / 2
            y = sum(p.y for p in point_coordinates) / 2
            self._midpoint = (x, y)
            logger.debug(f"Midpoint for Line cell {self._index}: {self._midpoint}")
            return self._midpoint
        except Exception as e:
            logger.error(f"Error calculating midpoint for Line cell {self._index}: {e}")
            raise

    def calculate_velocity_field(self):
        try:
            x = self._midpoint[0]
            y = self._midpoint[1]
            self._velocity_field = (y - (0.2*x), -x)
            logger.debug(f"Velocity field for Line cell {self._index}: {self._velocity_field}")
            return self._velocity_field
        except Exception as e:
            logger.error(f"Error calculating velocity field for Line cell {self._index}: {e}")
            raise
    
    def is_boundary(self):
        return True  
    
    @property
    def midpoint(self):
        return self._midpoint
    
    @property
    def velocity_field(self):
        return self._velocity_field
    
    @property
    def oil_amount(self):
        return self._oil_amount

    def __str__(self):
        neighbour_indices = [n.index for n in self._neighbours]
        return f"Line(index={self._index}, boundary={self.is_boundary()}, neighbours={neighbour_indices})"