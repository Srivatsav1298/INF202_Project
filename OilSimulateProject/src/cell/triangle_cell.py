from .base_cell import Cell, Point
import math
import numpy as np

class Triangle(Cell):
    def __init__(self, index, points=None, mesh=None, neighbours=None):
        super().__init__(index, points, mesh, neighbours)
        self._area = None
        self._velocityfield = None
<<<<<<< HEAD
        self._oil_intensity = None
        self._edge_vectors = None
        self._normal_vectors = None
        self._scaled_normals = None
=======
        self._outward_normals = []
>>>>>>> origin/main

    def calculate_midpoint(self):
        if self._midpoint is None:
            point_coordinates = [self._mesh.points[i] for i in self._points]
            x = sum(p.x for p in point_coordinates) / 3
            y = sum(p.y for p in point_coordinates) / 3
            self._midpoint = Point(x, y)
        return self._midpoint
<<<<<<< HEAD

    def calculate_velocity_field(self, point):
        """Calculate velocity field at a given point according to v(x) = [y - 0.2x, -x]"""
        x, y = point.x, point.y
        return Point(y - 0.2*x, -x)

    def calculate_edge_vectors(self):
        """Calculate edge vectors for the triangle"""
        if self._edge_vectors is None:
            points = [self._mesh.points[i] for i in self._points]
            self._edge_vectors = []
            for i in range(3):
                p1 = points[i]
                p2 = points[(i + 1) % 3]
                self._edge_vectors.append(Point(p2.x - p1.x, p2.y - p1.y))
        return self._edge_vectors

    def calculate_normal_vectors(self):
        """Calculate unit normal vectors for each edge"""
        if self._normal_vectors is None:
            edges = self.calculate_edge_vectors()
            self._normal_vectors = []
            for edge in edges:
                # Calculate normal vector (-y, x) and normalize it
                length = math.sqrt(edge.x**2 + edge.y**2)
                self._normal_vectors.append(Point(-edge.y/length, edge.x/length))
        return self._normal_vectors

    def calculate_scaled_normals(self):
        """Calculate scaled normal vectors ⃗ν_i,ℓ"""
        if self._scaled_normals is None:
            edges = self.calculate_edge_vectors()
            normals = self.calculate_normal_vectors()
            self._scaled_normals = []
            for edge, normal in zip(edges, normals):
                edge_length = math.sqrt(edge.x**2 + edge.y**2)
                self._scaled_normals.append(Point(normal.x * edge_length, normal.y * edge_length))
        return self._scaled_normals

    def calculate_flux(self, neighbor, edge_idx, dt):
        """Calculate flux across an edge with a neighboring cell"""
        if not hasattr(neighbor, 'oil_intensity'):  # Skip if neighbor is a line cell
            return 0.0
        
        # Get scaled normal for this edge
        scaled_normals = self.calculate_scaled_normals()
        nu = scaled_normals[edge_idx]
        
        # Calculate average velocity at the edge
        v_self = self.calculate_velocity_field(self.calculate_midpoint())
        v_ngh = self.calculate_velocity_field(neighbor.calculate_midpoint())
        v_avg = Point((v_self.x + v_ngh.x)/2, (v_self.y + v_ngh.y)/2)
        
        # Calculate dot product ⟨⃗v,⃗ν⟩
        v_dot_nu = v_avg.x * nu.x + v_avg.y * nu.y
        
        # Apply the g function
        if v_dot_nu > 0:
            g_value = self._oil_intensity * v_dot_nu
        else:
            g_value = neighbor.oil_intensity * v_dot_nu
        
        # Calculate flux
        return -(dt / self.calculate_area()) * g_value

    def calculate_area(self):
        if self._area is None:
            point_coordinates = [self._mesh.points[i] for i in self._points]
            x1, y1 = point_coordinates[0].x, point_coordinates[0].y
            x2, y2 = point_coordinates[1].x, point_coordinates[1].y
            x3, y3 = point_coordinates[2].x, point_coordinates[2].y
            self._area = 0.5 * abs(
                x1*(y2-y3) + x2*(y3-y1) + x3*(y1-y2)
            )
        return self._area

    def calculate_oil_intensity(self, oil_spill_center):
        self._oil_intensity = math.exp(
            -((self.calculate_midpoint().x - oil_spill_center[0])**2 + 
              (self.calculate_midpoint().y - oil_spill_center[1])**2) / 0.01
        )
        return self._oil_intensity

    def update_oil_intensity(self, new_intensity):
        """Update the oil intensity for the next time step"""
        self._oil_intensity = new_intensity

    @property
    def oil_intensity(self):
        return self._oil_intensity
    
=======
    
    def calculate_oil_amount(self, oil_spill_center):
        midpoint = self.calculate_midpoint()
        self._oil_amount = math.exp(- ((midpoint.x - oil_spill_center[0])**2 + (midpoint.y - oil_spill_center[1])**2) / (0.01))
        return self._oil_amount

    def calculate_area(self):
        point_coordinates = [self._mesh.points[i] for i in self._points]
        x1, y1 = point_coordinates[0].x, point_coordinates[0].y
        x2, y2 = point_coordinates[1].x, point_coordinates[1].y
        x3, y3 = point_coordinates[2].x, point_coordinates[2].y

        self._area = 0.5 * abs(
            (x1-x3)*(y2-y1) - (x1-x2)*(y3-y1)
        )
        
        return self._area
    
    def calculate_velocity_field(self):
        self.calculate_midpoint()
        x = self._midpoint.x
        y = self._midpoint.y
        self._velocityfield = (y - (0.2*x), -x)
        return self._velocityfield

    def store_outward_normals(self):
        for i, edge in enumerate(self._edge_vectors):
            perp_vector = np.array([-edge[1], edge[0]])
            normal = perp_vector / np.linalg.norm(perp_vector)

            midpoint = np.array([self.calculate_midpoint().x, self.calculate_midpoint().y])
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

>>>>>>> origin/main
    def __str__(self):
        """String representation of the Triangle cell"""
        neighbour_indices = [n.index for n in self._neighbours]
        midpoint = self.calculate_midpoint()
        return (
            f"Triangle(index={self._index}, "
            f"boundary={self.is_boundary()}, "
            f"neighbours={neighbour_indices}, "
            f"area={self.calculate_area():.4g}, "
            f"midpoint=({midpoint.x:.4g}, {midpoint.y:.4g}))"
        )