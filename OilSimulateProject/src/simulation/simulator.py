import numpy as np
import os
import logging
from ..visualization.plotter import Animation

logger = logging.getLogger(__name__)

class Simulation:
    def __init__(self, mesh, oil_spill_center, fishing_grounds, nSteps, tStart, tEnd, fps):
        self._mesh = mesh
        self._oil_spill_center = oil_spill_center
        self._fishing_grounds = fishing_grounds
        self._nSteps = nSteps
        self._tStart = tStart
        self._tEnd = tEnd
        self._fps = fps
        self._delta_t = self._tEnd/self._nSteps

        # Finding first frame when tStart is not 0
        self._nStart = round((self._tStart/self._tEnd) * self._nSteps)
        
        logger.debug(f"Simulation parameters set: nSteps={self._nSteps}, tStart={self._tStart}, tEnd={self._tEnd}, delta_t={self._delta_t:.3f}")

        self.initialize_oil_spill()
        self.run_simulation()

    def initialize_oil_spill(self):
        logger.info("Initializing oil spill distribution...")
        from ..cell.triangle_cell import Triangle
        for cell in self._mesh.cells:
            if isinstance(cell, Triangle):
                cell.calculate_oil_amount(self._oil_spill_center)

    def run_simulation(self):
        oil_animation = Animation(self._mesh, self._fps, self._fishing_grounds)
            
        # Render the first frame if tStart is 0
        if (self._tStart == 0) and (self._fps is not None):
            oil_animation.render_frame(0, 0, 0)

        for n in range(self._nSteps):
            logger.debug(f"Running step {n+1}/{self._nSteps} at time t={n*self._delta_t:.3f}s")
            self.oil_movement()
            total_oil_in_fishing_grounds = self.check_fishing_grounds(n)
            current_time = n * self._delta_t

            # logic for rendering first frame based on tStart
            if (self._tStart == 0) and (self._fps is not None):
                oil_animation.render_frame(
                    frame_index = n+1,
                    time_val = current_time,
                    total_oil = total_oil_in_fishing_grounds
                    )
            elif (n >= self._nStart) and (self._fps is not None):
                oil_animation.render_frame(
                    frame_index = n-self._nStart,
                    time_val = current_time,
                    total_oil = total_oil_in_fishing_grounds     
                    )
                
            if n == (self._nSteps-1):
                oil_animation.make_plot(
                    frame_index = n-self._nStart,
                    time_val = current_time,
                    total_oil = total_oil_in_fishing_grounds     
                    )

        
        if self._fps is not None:
            oil_animation.create_gif()

    def oil_movement(self):
        logger.debug("Updating oil movement across cells...")
        from ..cell.triangle_cell import Triangle
        for cell in self._mesh.cells:
            oil_over_each_facet = []
            if isinstance(cell, Triangle):
                for i, ngh in enumerate(cell.neighbours):
                    v_i = np.array(cell.velocity_field)
                    delta_t = self._delta_t
                    A_i = cell.area
                    u_i = cell.oil_amount
                    u_ngh = ngh.oil_amount
                    v_ngh = np.array(ngh.velocity_field)
                    v_avg = 0.5 * (v_i + v_ngh)

                    v_vector = cell.outward_normals[i] * np.linalg.norm(cell.edge_vectors[i])
                        
                    f = -((delta_t/A_i)*self.g(u_i, u_ngh, v_vector, v_avg))
                    oil_over_each_facet.append(f)
                    
                # Log flux changes
                logger.debug(f"Oil flux for cell {cell.index} and its neighbours: {oil_over_each_facet}")
                
                cell.update_oil_amount(oil_over_each_facet)

    def check_fishing_grounds(self, n):
        total_oil_in_fishing_grounds = 0
        for cell in self._mesh.cells:
            x, y = cell.midpoint[0], cell.midpoint[1]
            x_min, x_max = self._fishing_grounds[0]
            y_min, y_max = self._fishing_grounds[1]

            if x_min <= x <= x_max and y_min <= y <= y_max:
                total_oil_in_fishing_grounds += cell.oil_amount
        
        print(f"Oil in fishing grounds at t = {n*self._delta_t:.3f}: {total_oil_in_fishing_grounds:.4g}", end='\r')
        logger.info(f"Oil in fishing grounds at t = {n*self._delta_t:.3f}s: {total_oil_in_fishing_grounds:.4g}")
        
        return total_oil_in_fishing_grounds


    def g(self, u_i, u_ngh, v_vector, v_avg):
        dot_product = np.dot(v_vector, v_avg)
        if dot_product > 0:
            return u_i * dot_product
        else:
            return u_ngh * dot_product
        
    def save_solution(self, filename):
        logger.info(f"Saving simulation state to {filename}...")
        """Save the simulation state to a text file, including metadata."""
        metadata = {
            "tStart": self._tStart,
            "tEnd": self._tEnd,
            "nSteps": self._nSteps,
            "oil_spill_center": self._oil_spill_center,
        }
        try:
            with open(filename, "w") as f:
                f.write(f"# Metadata: {metadata}\n")
                for cell in self._mesh.cells:
                    if hasattr(cell, "oil_amount"):
                        f.write(f"{cell.index},{cell.oil_amount}\n")
            logger.info(f"Simulation state successfully saved to {filename}.")
        except Exception as e:
            logger.error(f"Failed to save simulation state: {e}")
            
    def load_solution(self, filename):
        logger.info(f"Loading simulation state from {filename}...")
        """Load the simulation state from a text file."""
        oil_data = {}
        try:
            with open(filename, "r") as f:
                for line in f:
                    if line.startswith("#"):  # Skip metadata
                        continue
                    index, oil_amount = line.strip().split(",")
                    oil_data[int(index)] = float(oil_amount)
            for cell in self._mesh.cells:
                if cell.index in oil_data:
                    cell._oil_amount = oil_data[cell.index]
            logger.info(f"Simulation state successfully loaded from {filename}.")
        except Exception as e:
            logger.error(f"Failed to load simulation state: {e}")