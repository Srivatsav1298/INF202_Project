import numpy as np
import os
import logging
from ..visualization.plotter import Animation

class Simulation:
    def __init__(self, mesh, oil_spill_center, nSteps, tStart, tEnd, fps, write_frequency, restart_file, log_file="logfile.log"):
        self._mesh = mesh
        self._oil_spill_center = oil_spill_center
        self._nSteps = nSteps
        self._tStart = tStart
        self._tEnd = tEnd
        self._fps = fps
        self._delta_t = (self._tEnd - self._tStart) / self._nSteps
        self._write_frequency = write_frequency
        self._restart_file = restart_file

        logging.basicConfig(filename=log_file, level=logging.INFO)
        self.logger = logging.getLogger("Simulation")
        self.log_simulation_parameters()

        if restart_file:
            self.load_solution(restart_file)
    
    def log_simulation_parameters(self):
        self.logger.info("Simulation Parameters:")
        self.logger.info(f"nSteps: {self._nSteps}, tStart: {self._tStart}, tEnd: {self._tEnd}, fps: {self._fps}")
        self.logger.info(f"Oil Spill Center: {self._oil_spill_center}")

    def log_oil_amount(self, time_step):
        total_oil = sum(cell.oil_amount for cell in self._mesh.cells if hasattr(cell, "oil_amount"))
        self.logger.info(f"Time {time_step:.2f}: Total Oil Amount = {total_oil:.4f}")

    def initialize_oil_spill(self):
        from ..cell.triangle_cell import Triangle
        for cell in self._mesh.cells:
            if isinstance(cell, Triangle):
                cell.calculate_oil_amount(self._oil_spill_center)

    def oil_movement(self):
        from ..cell.triangle_cell import Triangle

        oil_animation = Animation(self._mesh, self._fps)

        for n in range(self._nSteps):
            time_step = n * self._delta_t
            print(f"Calculating for t = {time_step:.4g}", end='\r')
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
                            
                            f = -((delta_t / A_i) * self.g(u_i, u_ngh, v_vector, v_avg))
                            oil_over_each_facet.append(f)
                    cell.update_oil_amount(oil_over_each_facet)

            if n % self._write_frequency == 0:
                self.save_solution(f"output/restart_t{time_step:.4g}.txt")

            oil_animation.render_frame(n)
        
        oil_animation.create_gif()

                
    def g(self, u_i, u_ngh, v_vector, v_avg):
        dot_product = np.dot(v_vector, v_avg)
        if dot_product > 0:
            return u_i * dot_product
        else:
            return u_ngh * dot_product
        
    def save_solution(self, filename):
        """Save the simulation state to a text file, including metadata."""
        metadata = {
            "tStart": self._tStart,
            "tEnd": self._tEnd,
            "nSteps": self._nSteps,
            "oil_spill_center": self._oil_spill_center,
        }
        with open(filename, "w") as f:
            f.write(f"# Metadata: {metadata}\n")
            for cell in self._mesh.cells:
                if hasattr(cell, "oil_amount"):
                    f.write(f"{cell.index},{cell.oil_amount}\n")

    def load_solution(self, filename):
        """Load the simulation state from a text file."""
        oil_data = {}
        with open(filename, "r") as f:
            for line in f:
                if line.startswith("#"):  # Skip metadata
                    continue
                index, oil_amount = line.strip().split(",")
                oil_data[int(index)] = float(oil_amount)
        for cell in self._mesh.cells:
            if cell.index in oil_data:
                cell._oil_amount = oil_data[cell.index]