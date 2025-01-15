from .base_cell import Cell
import math
import numpy as np

class Triangle(Cell):
    def __init__(self, index, points=None, mesh=None, neighbours=None):
        super().__init__(index, points, mesh, neighbours)
        self._midpoint = self.calculate_midpoint()
        self._area = self.calculate_area()
        self._velocityfield = self.calculate_velocity_field()
        self._outward_normals = []

    def calculate_midpoint(self):
        from ..io.mesh_reader import Point
        point_coordinates = [self._mesh.points[i] for i in self._points]
        x = sum(p.x for p in point_coordinates) / 3
        y = sum(p.y for p in point_coordinates) / 3
        self._midpoint = Point(x, y)
        return self._midpoint

    def calculate_area(self):
        point_coordinates = [self._mesh.points[i] for i in self._points]
        x1, y1 = point_coordinates[0].x, point_coordinates[0].y
        x2, y2 = point_coordinates[1].x, point_coordinates[1].y
        x3, y3 = point_coordinates[2].x, point_coordinates[2].y

        self._area = 0.5 * abs(
            (x1-x3)*(y2-y1) - (x1-x2)*(y3-y1)
        )
        
        return self._area
    
    def calculate_oil_amount(self, oil_spill_center):
        midpoint = self._midpoint
        self._oil_amount = math.exp(- ((midpoint.x - oil_spill_center.x)**2 + (midpoint.y - oil_spill_center.y)**2) / (0.01))
        return self._oil_amount


    def calculate_velocity_field(self):
        x = self._midpoint.x
        y = self._midpoint.y
        self._velocityfield = (y - (0.2*x), -x)
        return self._velocityfield

    def store_outward_normals(self):
        for i, edge in enumerate(self._edge_vectors):
            perp_vector = np.array([-edge[1], edge[0]])
            normal = perp_vector / np.linalg.norm(perp_vector)

            midpoint = np.array([self._midpoint.x, self._midpoint.y])
            p = np.array([self._edge_points[i][0].x, self._edge_points[i][0].y])

            to_p = p - midpoint

            if np.dot(normal, to_p) < 0:
                normal = -normal

            self._outward_normals.append(normal)
    
    def update_oil_amount(self, oil_over_each_facet):
        oil_loss = sum(oil_over_each_facet)
        new_oil_amount = self._oil_amount + oil_loss
        self._oil_amount = new_oil_amount
    
    @property
    def oil_amount(self):
        return self._oil_amount
    
    @property
    def outward_normals(self):
        return self._outward_normals
    
    @property
    def velocityfield(self):
        return self._velocityfield

    @property
    def area(self):
        return self._area

    def __str__(self):
        neighbour_indices = [n.index for n in self._neighbours]
        midpoint = self._midpoint
        return (
    f"Triangle(index={self._index}, "
    f"boundary={self.is_boundary()}, "
    f"neighbours={neighbour_indices}, "
    f"area={self.area:.4g}, "
    f"midpoint=({midpoint._x:.4g}, {midpoint._y:.4g}))"
)