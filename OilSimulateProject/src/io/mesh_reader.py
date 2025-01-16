import meshio
from ..cell.base_cell import Point, CellFactory
import concurrent.futures

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
                # Skip other cell types
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

        def process_cell(i, cell):
            cell.store_neighbours()

            # Print progress at intervals
            if i % print_interval == 0 or i == total_cells - 1:
                progress = (i + 1) / total_cells * 100
                print(f"Progress: {progress:.2f}% ({i + 1}/{total_cells})", end='\r')

        # Parallelizing with ProcessPoolExecutor if the task is CPU-bound
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = [executor.submit(process_cell, i, cell) for i, cell in enumerate(self._cells)]
            # Wait for all futures to complete
            concurrent.futures.wait(futures)

        print("\nDone.")

    def find_outward_normals(self):
        from ..cell.triangle_cell import Triangle

        print(f"Storing outward normals for each triangle in {self._file_name}:")

        def process_triangle(cell):
            if isinstance(cell, Triangle):
                cell.store_outward_normals()

        # Parallelizing outward normal calculation (adjust if task is CPU-bound or I/O-bound)
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = [executor.submit(process_triangle, cell) for cell in self._cells]
            # Wait for all futures to complete
            concurrent.futures.wait(futures)

