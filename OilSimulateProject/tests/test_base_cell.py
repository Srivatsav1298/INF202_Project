import pytest
from abc import ABCMeta
from src.cell.base_cell import Cell, CellFactory
from src.cell.line_cell import Line
from src.cell.triangle_cell import Triangle

class TestBaseCell:
    @pytest.fixture
    def mock_mesh(self):
        """Creates a mock mesh object with necessary attributes for testing."""
        class MockMesh:
            def __init__(self):
                self.cells = []
                self.points = [
                    MockPoint(0, 0),
                    MockPoint(1, 0),
                    MockPoint(0, 1),
                    MockPoint(1, 1)
                ]

        class MockPoint:
            def __init__(self, x, y):
                self.x = x
                self.y = y

        return MockMesh()

    def test_cell_abstract_methods(self):
        """Ensure that Cell cannot be instantiated directly and requires abstract methods."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class Cell"):
            Cell(0, [], None)

    def test_cell_properties(self, mock_mesh):
        """Test the behavior of properties in a subclass of Cell."""

        class MockCell(Cell):
            def calculate_midpoint(self):
                return 0, 0

            def calculate_velocity_field(self):
                pass

            def store_neighbours_and_edges(self):
                pass

            def store_outward_normals(self):
                pass

            def is_boundary(self):
                return False

            def __str__(self):
                return "MockCell"

        cell = MockCell(1, [0, 1, 2], mock_mesh)

        # Validate property values
        assert cell.index == 1, "Index property mismatch."
        assert cell.points == [0, 1, 2], "Points property mismatch."
        assert cell.oil_amount == 0, "Default oil amount should be zero."
        assert cell.neighbours == [], "Neighbours property should be empty by default."
        assert cell.edge_vectors == [], "Edge vectors property should be empty by default."

    @pytest.mark.parametrize("cell_points, cell_type, expected_class", [
        ([0, 1], "line", Line),
        ([0, 1, 2], "triangle", Triangle)
    ])
    def test_cell_factory_creation(self, mock_mesh, cell_points, cell_type, expected_class):
        """Test that CellFactory correctly creates instances of supported cell types."""
        factory = CellFactory()

        # Create cell using the factory and validate type
        cell = factory(cell_points, cell_type, 0, mock_mesh)
        assert isinstance(cell, expected_class), f"Expected {expected_class}, got {type(cell)}."
        assert cell.points == cell_points, "Points property mismatch in created cell."

    def test_cell_factory_invalid_type(self, mock_mesh):
        """Ensure that CellFactory raises an error for unsupported cell types."""
        factory = CellFactory()

        with pytest.raises(ValueError, match="Unknown cell type: hexagon"):
            factory([0, 1, 2], "hexagon", 2, mock_mesh)
