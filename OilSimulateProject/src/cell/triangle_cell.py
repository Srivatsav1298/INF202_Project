from .base_cell import Cell
import math
import numpy as np
import logging

logger = logging.getLogger(__name__)

class Triangle(Cell):
    def __init__(self, index, points=None, mesh=None, neighbours=None):
        logger.debug(f"Initializing Triangle cell with index {index}")
        super().__init__(index, points, mesh, neighbours)
        self._midpoint = self.calculate_midpoint()
        self._area = self.calculate_area()
        self._velocity_field = self.calculate_velocity_field()
        self._outward_normals = []

    def store_neighbours_and_edges(self):
        logger.info(f"Storing neighbors and edges for Triangle cell {self._index}")
        try:
            self_set = set(self._points)
            for cell in self._mesh.cells:
                point_set = set(cell.points)
                matching_points = point_set.intersection(self_set)
                point_coordinates = [self._mesh.points[i] for i in matching_points]

                if len(matching_points) == 2:
                    self._neighbours.append(cell)
                    self._edge_vectors.append([
                        point_coordinates[0].x - point_coordinates[1].x,
                        point_coordinates[0].y - point_coordinates[1].y])
                    self._edge_points.append(point_coordinates)
        except Exception as e:
            logger.error(f"Error storing neighbors for Triangle cell {self._index}: {e}")
            raise    

    def calculate_midpoint(self):
        try:
            point_coordinates = [self._mesh.points[i] for i in self._points]
            x = sum(p.x for p in point_coordinates) / 3
            y = sum(p.y for p in point_coordinates) / 3
            self._midpoint = (x, y)
            logger.debug(f"Midpoint for Triangle cell {self._index}: {self._midpoint}")
            return self._midpoint
        except Exception as e:
            logger.error(f"Error calculating midpoint for Triangle cell {self._index}: {e}")
            raise

    def calculate_area(self):
        try:
            point_coordinates = [self._mesh.points[i] for i in self._points]
            x1, y1 = point_coordinates[0].x, point_coordinates[0].y
            x2, y2 = point_coordinates[1].x, point_coordinates[1].y
            x3, y3 = point_coordinates[2].x, point_coordinates[2].y

            area = 0.5 * abs(
                (x1-x3)*(y2-y1) - (x1-x2)*(y3-y1)
            )
            logger.debug(f"Area for Triangle cell {self._index}: {area:.4g}")
            return area
        except Exception as e:
            logger.error(f"Error calculating area for Triangle cell {self._index}: {e}")
            raise
    
    def calculate_oil_amount(self, oil_spill_center):
        try:
            midpoint = self._midpoint
            self._oil_amount = math.exp(- ((midpoint[0] - oil_spill_center[0])**2 + (midpoint[1] - oil_spill_center[1])**2) / (0.01))
            logger.debug(f"Oil amount for Triangle cell {self._index}: {self._oil_amount:.4g}")
            return self._oil_amount
        except Exception as e:
            logger.error(f"Error calculating oil amount for Triangle cell {self._index}: {e}")
            raise

    def calculate_velocity_field(self):
        x = self._midpoint[0]
        y = self._midpoint[1]
        self._velocity_field = (y - (0.2*x), -x)
        return self._velocity_field

    def store_outward_normals(self):
        logger.debug(f"Storing outward normals for Triangle cell {self._index}")
        try:
            for i, edge in enumerate(self._edge_vectors):
                perp_vector = np.array([-edge[1], edge[0]])
                normal = perp_vector / np.linalg.norm(perp_vector)

                midpoint = np.array([self._midpoint[0], self._midpoint[1]])
                p = np.array([self._edge_points[i][0].x, self._edge_points[i][0].y])

                to_p = p - midpoint

                if np.dot(normal, to_p) < 0:
                    normal = -normal

                self._outward_normals.append(normal)
        except Exception as e:
            logger.error(f"Error storing outward normals for Triangle cell {self._index}: {e}")
            raise
    
    def update_oil_amount(self, oil_over_each_facet):
        oil_loss = sum(oil_over_each_facet)
        new_oil_amount = self._oil_amount + oil_loss
        self._oil_amount = new_oil_amount

    def is_boundary(self):
        from .line_cell import Line
        if isinstance(self, Triangle):
            return any(isinstance(neighbor, Line) for neighbor in self._neighbours)
        return False
    
    @property
    def midpoint(self):
        return self._midpoint

    @property
    def oil_amount(self):
        return self._oil_amount
    
    @property
    def outward_normals(self):
        return self._outward_normals
    
    @property
    def velocity_field(self):
        return self._velocity_field

    @property
    def area(self):
        return self._area

    def __str__(self):
        """String representation of the Triangle cell"""
        neighbour_indices = [n.index for n in self._neighbours]
        midpoint = self._midpoint
        return (
    f"Triangle(index={self._index}, "
    f"boundary={self.is_boundary()}, "
    f"neighbours={neighbour_indices}, "
    f"area={self.area:.4g}, "
    f"midpoint=({midpoint[0]:.4g}, {midpoint[1]:.4g}))"
)
