import meshio
from ..cell.base_cell import Point, CellFactory

class Mesh:
    def __init__(self, file_name):
        self._file_name = file_name
        msh = meshio.read(file_name)

        # Read points (assumes 2D points)
        self._points = [Point(*point[:2]) for point in msh.points]

        # Read cells and create cell objects
        self._cells = []
        create_cell = CellFactory()
        index = 0
        for block in msh.cells:
            if block.type in ("line", "triangle"):
                for cell_points in block.data:
                    cell_obj = create_cell(cell_points, block.type, index, self)
                    self._cells.append(cell_obj)
                    index += 1
            else:
                # skip other cell types
                pass

    @property
    def cells(self):
        return self._cells

    @property
    def points(self):
        return self._points

    def find_neighbours(self):
        total_cells = len(self._cells)
        print_interval = max(1, total_cells // 100)  # Print progress every 1% of cells
        print(f"Storing neighbours for each cell in {self._file_name}:")

        for i, cell in enumerate(self._cells):
            cell.store_neighbours()

            # Print progress at intervals
            if i % print_interval == 0 or i == total_cells - 1:
                progress = (i + 1) / total_cells * 100
                print(f"Progress: {progress:.2f}% ({i + 1}/{total_cells})", end='\r')

        print("\nDone.")
