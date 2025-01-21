import numpy as np
import os
import logging
from ..visualization.plotter import Animation
import logging

logger = logging.getLogger(__name__)

class Simulation:
    """
    A class to simulate the movement of oil spills in a 2D mesh over time.

    Attributes:
        mesh: The computational mesh representing the simulation domain.
        oil_spill_center: Coordinates of the initial oil spill.
        fishing_grounds: Boundary coordinates of the fishing grounds.
        nSteps: Total number of simulation steps.
        tStart: Start time for the simulation.
        tEnd: End time for the simulation.
        fps: Frames per second for animation output.
        results_folder: Directory where simulation results are stored.
        restart_file: File containing oil values for the intial oil spill.
        config_name: The name of active toml file.
    """
    def __init__(
        self, mesh, oil_spill_center: tuple, fishing_grounds: tuple,
        nSteps: int, tStart: float, tEnd: float, fps: int,
        results_folder: str, restart_file: str, config_name: str):
        """
        Initializes the Simulation object with input parameters.
        """
        self._mesh = mesh
        self._oil_spill_center = oil_spill_center
        self._fishing_grounds = fishing_grounds
        self._nSteps = nSteps
        self._tStart = tStart
        self._tEnd = tEnd
        self._fps = fps
        self._delta_t = (self._tEnd - self._tStart) / self._nSteps
        self._results_folder = results_folder
        self._restart_file = restart_file
        self._config_name = config_name

        self.initialize_oil_spill()

    def initialize_oil_spill(self):
        """
        Initializes oil spill based on whether restart file is provided or not
        """
        # Use gaussian function if tStart = 0, and there's no restart file
        if self._restart_file is None:
            self.gaussian_based_oil_spill()
        else: # Use oil values from solution file
            from ..io.solution_reader import initialize_oil_spill
            initialize_oil_spill(self._mesh, self._restart_file)

    def gaussian_based_oil_spill(self):
        """
        Distributes the initial oil amount across the mesh based on proximity to the spill center.
        """
        print("Initializing oil spill")
        from ..cell.triangle_cell import Triangle
        for cell in self._mesh.cells:
            if isinstance(cell, Triangle):
                cell.calculate_oil_amount(self._oil_spill_center)
    
    def run_simulation(self):
        """
        Executes the simulation by iterating over time steps and rendering animation frames.
        """
        oil_animation = Animation(self._mesh, self._fps, self._fishing_grounds, self._results_folder)

        # Render the initial frame if write_frequency/fps is provided.
        if self._fps is not None:
            oil_animation.render_frame(
                time_val = self._tStart, 
                total_oil = self.check_fishing_grounds(0))

        # Calculate new oil spread for each step
        for n in range(self._nSteps+1):
            self.oil_movement()
            # Frames will be rendered if fps is defined.
            self.render_simulation_step(oil_animation, n)

        # Render videoanimation with generated frames if fps is defined.
        if self._fps is not None:
            oil_animation.create_gif()

    def oil_movement(self):
        """
        Calculates and updates the oil distribution across the mesh for one time step.
        """
        from ..cell.triangle_cell import Triangle
        for cell in self._mesh.cells:
            oil_flux = []
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
                    
                    # Compute flux through each facet
                    flux = -((delta_t / A_i) * self.g(u_i, u_ngh, v_vector, v_avg))
                    oil_flux.append(flux)

                # Update the cell's oil amount after processing all facets
                cell.update_oil_amount(oil_flux)

    def render_simulation_step(self, oil_animation: Animation, n: int):
        """
        Renders a single frame of the simulation if fps is provided,
        and writes a solution as well as final frame at last step

        Args:
            oil_animation: The Animation object handling rendering.
            n: Current time step index.
        """
        current_time = self._tStart + (n * self._delta_t)
        total_oil_in_fishing_grounds = self.check_fishing_grounds(n)
        logger.info(f"Time = {current_time:.3f} | Oil in Fishing Grounds = {total_oil_in_fishing_grounds:.2f}")

        # Render next frame is fps is provided.
        if self._fps is not None:
            oil_animation.render_frame(
                time_val = current_time, 
                total_oil = total_oil_in_fishing_grounds)

        # Final solution will always be stored
        if n == (self._nSteps):
            # Store image of final plot
            oil_animation.make_plot(
                time_val = current_time, 
                total_oil = total_oil_in_fishing_grounds)
            # Store oil amount for each cell as solution / restart file
            from ..io.solution_writer import write_solution
            write_solution(
                mesh = self._mesh,
                time_val = current_time, # this value tells the user what to use as tStart
                total_oil = total_oil_in_fishing_grounds,
                config_name = self._config_name)

    def check_fishing_grounds(self, n: int) -> float:
        """
        Calculates the total amount of oil within the fishing grounds at a given time step.

        Args:
            n: Current time step index.

        Returns:
            Total oil in the fishing grounds.
        """
        total_oil = 0
        for cell in self._mesh.cells:
            x, y = cell.midpoint
            x_min, x_max = self._fishing_grounds[0]
            y_min, y_max = self._fishing_grounds[1]

            if x_min <= x <= x_max and y_min <= y <= y_max:
                total_oil += cell.oil_amount

        print(f"Oil in fishing grounds at t = {self._tStart + (n * self._delta_t):.3f}: {total_oil:.4g}", end='\r')
        return total_oil

    def g(self, u_i: float, u_ngh: float, v_vector: np.ndarray, v_avg: np.ndarray) -> float:
        """
        Computes the flux function based on oil amounts and velocity fields.

        Args:
            u_i: Oil amount in the current cell.
            u_ngh: Oil amount in the neighboring cell.
            v_vector: Scaled outward normal vector.
            v_avg: Average velocity vector between the current and neighboring cells.

        Returns:
            Calculated flux value.
        """
        dot_product = np.dot(v_vector, v_avg)
        if dot_product > 0:
            return u_i * dot_product
        else:
            return u_ngh * dot_product
