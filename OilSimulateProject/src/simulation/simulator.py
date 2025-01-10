from ..cell.triangle_cell import Triangle

def initialize_oil_spill(mesh, oil_spill_center):
    for cell in mesh.cells:
        if isinstance(cell, Triangle):
            cell.calculate_oil_intensity(oil_spill_center)
        else:
            pass
    