import pytest
from src.cell.line_cell import Line
from src.cell.base_cell import Cell

class TestLineCell:
    @pytest.fixture
    def mock_mesh(self):
        """Creates a mock mesh object with necessary attributes for testing."""
        class MockMesh:
            def __init__(self):
                self.cells = []
                self.points = [
                    MockPoint(0, 0),
                    MockPoint(1, 0),
                    MockPoint(0, 1)
                ]

        class MockPoint:
            def __init__(self, x, y):
                self.x = x
                self.y = y

        return MockMesh()

    @pytest.fixture
    def line_cell(self, mock_mesh):
        """Creates a Line cell instance for testing."""
        return Line(0, [0, 1], mock_mesh)

    def test_line_cell_initialization(self, line_cell):
        """Test the initialization of a Line cell."""
        assert line_cell.index == 0, "Index should be initialized correctly."
        assert line_cell.points == [0, 1], "Points should be initialized correctly."
        assert line_cell.oil_amount == 0, "Oil amount for a Line cell should always be 0."
        assert line_cell.is_boundary() is True, "Line cells should always be boundary cells."

    def test_calculate_midpoint(self, line_cell):
        """Test the midpoint calculation of a Line cell."""
        midpoint = line_cell.calculate_midpoint()
        assert midpoint == (0.5, 0.0), "Midpoint calculation is incorrect."

    def test_calculate_velocity_field(self, line_cell):
        """Test the velocity field calculation for a Line cell."""
        velocity = line_cell.calculate_velocity_field()
        assert velocity == (line_cell.midpoint[1] - (0.2 * line_cell.midpoint[0]), -line_cell.midpoint[0]), "Velocity field calculation is incorrect."

    def test_store_neighbours_and_edges(self, mock_mesh):
        """Test storing neighbors and edges for Line cells."""
        # Create a few mock cells to test neighbor detection
        line1 = Line(0, [0, 1], mock_mesh)
        line2 = Line(1, [1, 2], mock_mesh)
        triangle = MockTriangle(2, [0, 1, 2], mock_mesh)

        mock_mesh.cells = [line1, line2, triangle]

        # Store neighbors and log output for debugging
        line1.store_neighbours_and_edges()

        # Debugging information
        print(f"Neighbors of Line1: {[type(n).__name__ for n in line1.neighbours]}")

        # Only Line cells should be neighbors
        expected_neighbors = [line2]

        assert len(line1.neighbours) == len(expected_neighbors), "Unexpected number of neighbors for Line1."
        assert set(line1.neighbours) == set(expected_neighbors), "Neighbor cells do not match expected values."



    def test_invalid_oil_amount(self, line_cell):
        """Ensure that setting a negative oil amount raises an error."""
        with pytest.raises(ValueError, match="Oil amount cannot be negative."):
            line_cell.oil_amount = -1

    def test_string_representation(self, line_cell):
        """Test the string representation of a Line cell."""
        expected_str = "Line(index=0, boundary=True, neighbours=[])"
        assert str(line_cell) == expected_str, "String representation is incorrect."

# Mock triangle class for testing purposes
class MockTriangle(Cell):
    def __init__(self, index, points, mesh):
        super().__init__(index, points, mesh)

    def calculate_midpoint(self):
        return 0.0, 0.0

    def calculate_velocity_field(self):
        pass

    def store_neighbours_and_edges(self):
        pass

    def store_outward_normals(self):
        pass

    def is_boundary(self):
        return False

    def __str__(self):
        return "MockTriangle"
