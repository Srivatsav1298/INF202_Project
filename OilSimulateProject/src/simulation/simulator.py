from ..cell.triangle_cell import Triangle
import numpy as np

class Simulation:
    def __init__(self, mesh, oil_spill_center, end_time=1.0, dt=0.01):
        self._mesh = mesh
        self._oil_spill_center = oil_spill_center
        self._end_time = end_time
        self._dt = dt
        self._current_time = 0.0
        self._timestep = 0

    def initialize_oil_spill(self):
        """Initialize the oil spill distribution"""
        for cell in self._mesh.cells:
            if isinstance(cell, Triangle):
                cell.calculate_oil_intensity(self._oil_spill_center)
            else:
                pass

    def step(self):
        """Perform one time step of the simulation"""
        # Store new intensities separately to avoid affecting other cells' calculations
        new_intensities = {}
        
        # Calculate new intensities for all triangle cells
        for cell in self._mesh.cells:
            if isinstance(cell, Triangle):
                total_flux = 0
                # Calculate flux across each edge with neighbors
                for idx, neighbor in enumerate(cell.neighbours):
                    flux = cell.calculate_flux(neighbor, idx, self._dt)
                    total_flux += flux
                
                # Calculate new intensity
                new_intensities[cell.index] = cell.oil_intensity + total_flux
        
        # Update all cells with their new intensities
        for cell in self._mesh.cells:
            if isinstance(cell, Triangle):
                cell.update_oil_intensity(new_intensities[cell.index])
        
        self._current_time += self._dt
        self._timestep += 1

    def run(self):
        """Run the full simulation"""
        while self._current_time < self._end_time:
            self.step()
            if self._timestep % 10 == 0:  # Print progress every 10 steps
                print(f"Time: {self._current_time:.3f} / {self._end_time:.3f}")