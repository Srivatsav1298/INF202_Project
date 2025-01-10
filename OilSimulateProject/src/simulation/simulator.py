class Simulation:
    def __init__(self, mesh, oil_spill_center):
        self._mesh = mesh
        self._oil_spill_center = oil_spill_center

    def initialize_oil_spill(self):
        from ..cell.triangle_cell import Triangle

        for cell in self._mesh.cells:
            if isinstance(cell, Triangle):
                cell.calculate_oil_intensity(self._oil_spill_center)
            else:
                pass
        

