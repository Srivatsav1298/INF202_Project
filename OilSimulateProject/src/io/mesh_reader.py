import meshio
from ..cell.base_cell import Point, CellFactory

class Mesh:
    def __init__(self, file_name):
        msh = meshio.read(file_name)

        # Read points (assumes 2D points)
        self._points = [Point(*point[:2]) for point in msh.points]

        # Read cells and create cell objects
        self._cells = []
        create_cell = CellFactory()
        index = 0
        for block in msh.cells:
            if block.type in ("line", "triangle"):
                for cell_data in block.data:
                    cell_obj = create_cell(cell_data, block.type, index, self)
                    self._cells.append(cell_obj)
                    index += 1
            else:
                # skip other cell types
                pass

    def get_cells(self):
        return self._cells

    def get_points(self):
        return self._points

    def find_neighbours(self):
        for cell in self._cells:
            cell.store_neighbours()