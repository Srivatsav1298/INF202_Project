import numpy as np
from ..visualization.plotter import Animation

class Simulation:
    def __init__(self, mesh, oil_spill_center, nSteps, tStart, tEnd, fps):
        self._mesh = mesh
        self._oil_spill_center = oil_spill_center
        self._nSteps = nSteps
        self._tStart = tStart
        self._tEnd = tEnd
        self._fps = fps
        self._delta_t = (self._tEnd-self._tStart)/self._nSteps

    def initialize_oil_spill(self):
        from ..cell.triangle_cell import Triangle
        for cell in self._mesh.cells:
            if isinstance(cell, Triangle):
                cell.calculate_oil_amount(self._oil_spill_center)

    def oil_movement(self):
        from ..cell.triangle_cell import Triangle

        oil_animation = Animation(self._mesh, self._fps)

        for n in range(self._nSteps):
            print(f"Calculating for t = {n*self._delta_t:.4g}", end='\r')
            for cell in self._mesh.cells:
                oil_over_each_facet = []
                if isinstance(cell, Triangle):
                    for i, ngh in enumerate(cell.neighbours):
                        if isinstance(ngh, Triangle):
                            delta_t = self._delta_t
                            v_i = np.array(cell.calculate_velocity_field())
                            v_ngh = np.array(ngh.calculate_velocity_field())
                            v_avg = 0.5 * (v_i + v_ngh)
                            A_i = cell.calculate_area()
                            u_i = cell.oil_amount
                            u_ngh = ngh.oil_amount
                            v_vector = cell.outward_normals[i] * np.linalg.norm(cell.edge_vectors[i])
                            
                            f = -((delta_t/A_i)*self.g(u_i, u_ngh, v_vector, v_avg))
                            oil_over_each_facet.append(f)
                    cell.update_oil_amount(oil_over_each_facet)
            oil_animation.render_frame(n)
        
        oil_animation.create_gif()

                
    def g(self, u_i, u_ngh, v_vector, v_avg):
        dot_product = np.dot(v_vector, v_avg)
        if dot_product > 0:
            return u_i * dot_product
        else:
            return u_ngh * dot_product
