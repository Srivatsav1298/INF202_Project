import pytest
from unittest.mock import MagicMock, patch
from src.io.mesh_reader import Mesh, Point

class TestMesh:
    @pytest.fixture
    def mock_meshio_data(self):
        """Creates a mock for meshio.read."""
        mock_msh = MagicMock()

        # Mock points
        mock_msh.points = [
            [0.0, 0.0],
            [1.0, 0.0],
            [0.0, 1.0],
            [1.0, 1.0]
        ]

        # Mock cells
        mock_msh.cells = [
            MagicMock(type="line", data=[[0, 1], [1, 2]]),
            MagicMock(type="triangle", data=[[0, 1, 2]])
        ]

        return mock_msh

    @pytest.fixture
    def mock_point(self):
        """Returns a Point instance for testing."""
        return Point(0.5, 0.5)

    @patch("src.io.mesh_reader.meshio.read")
    def test_initialize_points(self, mock_meshio_read, mock_meshio_data):
        """Test initialization of points in the Mesh class."""
        mock_meshio_read.return_value = mock_meshio_data

        mesh = Mesh("mock_file.msh")

        assert len(mesh.points) == len(mock_meshio_data.points), "The number of points should match the mock data."
        assert isinstance(mesh.points[0], Point), "Points should be initialized as Point instances."

    @patch("src.io.mesh_reader.meshio.read")
    def test_initialize_cells(self, mock_meshio_read, mock_meshio_data):
        """Test initialization of cells in the Mesh class."""
        mock_meshio_read.return_value = mock_meshio_data

        mesh = Mesh("mock_file.msh")

        assert len(mesh.cells) == len([cell for cell in mock_meshio_data.cells if cell.type in ["line", "triangle"]]), "The number of cells should match the mock data."
        assert mesh.cells[0].points == [0, 1], "Cell points do not match the mock data."

    @patch("src.io.mesh_reader.meshio.read")
    def test_skip_unsupported_cells(self, mock_meshio_read, mock_meshio_data):
        """Test that unsupported cell types are skipped during initialization."""
        # Add unsupported cell type to mock data
        mock_meshio_data.cells.append(MagicMock(type="quad", data=[[0, 1, 2, 3]]))
        mock_meshio_read.return_value = mock_meshio_data

        mesh = Mesh("mock_file_with_unsupported.msh")

        supported_types = ["line", "triangle"]
        actual_cells = [cell for cell in mesh.cells if cell.__class__.__name__.lower() in supported_types]
        assert len(actual_cells) == len([cell for cell in mock_meshio_data.cells if cell.type in supported_types]), "Unsupported cell types should be skipped."

    @pytest.mark.parametrize("point_data, expected_x, expected_y", [
        ([1.5, 2.5], 1.5, 2.5),
        ([0.0, 0.0], 0.0, 0.0),
        ([-1.0, -1.0], -1.0, -1.0)
    ])
    def test_point_initialization(self, point_data, expected_x, expected_y):
        """Test the initialization of the Point class."""
        point = Point(*point_data)

        assert point.x == expected_x, "X-coordinate is not initialized correctly."
        assert point.y == expected_y, "Y-coordinate is not initialized correctly."

    @patch("src.io.mesh_reader.Mesh.find_neighbours_and_edges")
    @patch("src.io.mesh_reader.Mesh.find_outward_normals")
    @patch("src.io.mesh_reader.meshio.read")
    def test_mesh_methods_called(self, mock_meshio_read, mock_find_normals, mock_find_neighbors, mock_meshio_data):
        """Test that mesh methods for neighbors and normals are called during initialization."""
        mock_meshio_read.return_value = mock_meshio_data

        Mesh("mock_file.msh")

        mock_find_neighbors.assert_called_once(), "find_neighbours_and_edges should be called once."
        mock_find_normals.assert_called_once(), "find_outward_normals should be called once."

    @patch("src.io.mesh_reader.meshio.read")
    def test_find_neighbours_and_edges(self, mock_meshio_read, mock_meshio_data):
        """Test the find_neighbours_and_edges method in the Mesh class."""
        mock_meshio_read.return_value = mock_meshio_data

        mesh = Mesh("mock_file.msh")

        first_cell = MagicMock()
        first_cell.store_neighbours_and_edges = MagicMock()
        mesh._cells = [first_cell]

        mesh.find_neighbours_and_edges()

        first_cell.store_neighbours_and_edges.assert_called_once(), "Neighbor detection for the first cell should be called."

    @patch("src.io.mesh_reader.meshio.read")
    def test_find_outward_normals(self, mock_meshio_read, mock_meshio_data):
        """Test the find_outward_normals method in the Mesh class."""
        mock_meshio_read.return_value = mock_meshio_data

        mesh = Mesh("mock_file.msh")

        first_cell = MagicMock()
        first_cell.store_outward_normals = MagicMock()
        mesh._cells = [first_cell]

        mesh.find_outward_normals()

        first_cell.store_outward_normals.assert_called_once(), "Outward normal calculation for the first cell should be called."
