import pytest
import numpy as np
from src.cell.triangle_cell import Triangle
from src.cell.line_cell import Line

@pytest.fixture
def simple_mesh():
    """Create a simple mesh with one triangle for basic tests."""
    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    class MockMesh:
        def __init__(self):
            self.points = [
                Point(0, 0),  # point 0
                Point(1, 0),  # point 1
                Point(0, 1)   # point 2
            ]
            self.cells = []

    return MockMesh()

@pytest.fixture
def basic_triangle(simple_mesh):
    """Create a basic triangle with known coordinates for testing."""
    triangle = Triangle(0, [0, 1, 2], simple_mesh)
    simple_mesh.cells.append(triangle)
    return triangle

def test_triangle_initialization(basic_triangle):
    """Test if triangle is initialized correctly with basic properties."""
    assert basic_triangle.index == 0
    assert basic_triangle.points == [0, 1, 2]
    assert isinstance(basic_triangle.midpoint, tuple)
    assert isinstance(basic_triangle.area, float)
    assert isinstance(basic_triangle.velocity_field, tuple)

def test_triangle_midpoint_calculation(basic_triangle):
    """Test if midpoint is calculated correctly for a simple triangle."""
    expected_x = (0 + 1 + 0) / 3  # Average of x coordinates
    expected_y = (0 + 0 + 1) / 3  # Average of y coordinates
    assert basic_triangle.midpoint[0] == pytest.approx(expected_x)
    assert basic_triangle.midpoint[1] == pytest.approx(expected_y)

def test_triangle_area_calculation(basic_triangle):
    """Test if area is calculated correctly for a simple triangle."""
    # Area should be 0.5 for our simple triangle (base=1, height=1)
    assert basic_triangle.area == pytest.approx(0.5)

def test_velocity_field_calculation(basic_triangle):
    """Test if velocity field is calculated correctly at midpoint."""
    midpoint = basic_triangle.midpoint
    expected_vx = midpoint[1] - (0.2 * midpoint[0])
    expected_vy = -midpoint[0]
    assert basic_triangle.velocity_field[0] == pytest.approx(expected_vx)
    assert basic_triangle.velocity_field[1] == pytest.approx(expected_vy)

@pytest.mark.parametrize("oil_amount,should_raise", [
    (1.0, False),
    (0.0, False),
    (-1.0, True)
])
def test_oil_amount_validation(basic_triangle, oil_amount, should_raise):
    """Test oil amount setter with valid and invalid values."""
    if should_raise:
        with pytest.raises(ValueError):
            basic_triangle.oil_amount = oil_amount
    else:
        basic_triangle.oil_amount = oil_amount
        assert basic_triangle.oil_amount == oil_amount

def test_calculate_oil_amount(basic_triangle):
    """Test oil amount calculation for a specific spill center."""
    oil_spill_center = (0.35, 0.45)
    oil_amount = basic_triangle.calculate_oil_amount(oil_spill_center)
    assert isinstance(oil_amount, float)
    assert oil_amount >= 0

def test_update_oil_amount(basic_triangle):
    """Test updating oil amount with facet values."""
    initial_oil = 1.0
    basic_triangle.oil_amount = initial_oil
    oil_changes = [0.1, -0.2, 0.3]
    
    basic_triangle.update_oil_amount(oil_changes)
    expected_oil = initial_oil + sum(oil_changes)
    assert basic_triangle.oil_amount == pytest.approx(expected_oil)

def test_str_representation(basic_triangle):
    """Test string representation of triangle."""
    str_rep = str(basic_triangle)
    assert isinstance(str_rep, str)
    assert "Triangle" in str_rep
    assert str(basic_triangle.index) in str_rep
    assert str(round(basic_triangle.area, 4)) in str_rep
    
@pytest.fixture
def mesh_with_neighbors():
    """Create a mesh with multiple cells for neighbor testing."""
    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    class MockMesh:
        def __init__(self):
            self.points = [
                Point(0, 0),   # point 0
                Point(1, 0),   # point 1
                Point(0, 1),   # point 2
                Point(1, 1)    # point 3
            ]
            self.cells = []

    return MockMesh()

def test_store_neighbours_and_edges(mesh_with_neighbors):
    """Test if neighbors and edges are correctly stored for a triangle."""
    # Create two adjacent triangles
    triangle1 = Triangle(0, [0, 1, 2], mesh_with_neighbors)
    triangle2 = Triangle(1, [1, 2, 3], mesh_with_neighbors)
    
    # Add triangles to mesh
    mesh_with_neighbors.cells.extend([triangle1, triangle2])
    
    # Store neighbors for first triangle
    triangle1.store_neighbours_and_edges()
    
    # Verify neighbors are stored
    assert len(triangle1._neighbours) == 1
    assert triangle1._neighbours[0] == triangle2
    
    # Verify edge vectors are stored
    assert len(triangle1._edge_vectors) == 1
    assert len(triangle1._edge_points) == 1

def test_boundary_detection(mesh_with_neighbors):
    """Test boundary detection with different cell configurations."""
    # Create triangle and line cells
    triangle = Triangle(0, [0, 1, 2], mesh_with_neighbors)
    line = Line(1, [0, 1], mesh_with_neighbors)
    
    # Add cells to mesh
    mesh_with_neighbors.cells.extend([triangle, line])
    
    # Store neighbors
    triangle.store_neighbours_and_edges()
    
    # Test boundary detection
    assert triangle.is_boundary() == True
    
    # Create a new mesh for non-boundary configuration
    class MockMesh:
        def __init__(self):
            self.points = mesh_with_neighbors.points
            self.cells = []
            
    mesh_without_line = MockMesh()
    triangle_non_boundary = Triangle(0, [0, 1, 2], mesh_without_line)
    triangle2 = Triangle(1, [1, 2, 3], mesh_without_line)
    mesh_without_line.cells.extend([triangle_non_boundary, triangle2])
    
    triangle_non_boundary.store_neighbours_and_edges()
    assert triangle_non_boundary.is_boundary() == False

def test_outward_normals_calculation(mesh_with_neighbors):
    """Test calculation of outward normal vectors."""
    # Create triangle with neighbors
    triangle1 = Triangle(0, [0, 1, 2], mesh_with_neighbors)
    triangle2 = Triangle(1, [1, 2, 3], mesh_with_neighbors)
    mesh_with_neighbors.cells.extend([triangle1, triangle2])
    
    # Store neighbors and calculate normals
    triangle1.store_neighbours_and_edges()
    triangle1.store_outward_normals()
    
    # Verify normals exist and are unit vectors
    assert len(triangle1.outward_normals) > 0
    for normal in triangle1.outward_normals:
        # Check if it's a unit vector
        assert pytest.approx(np.linalg.norm(normal)) == 1.0
        # Check if it's perpendicular to its edge
        assert len(normal) == 2  # 2D vector

def test_complex_neighbor_interaction(mesh_with_neighbors):
    """Test interaction between multiple triangles sharing edges."""
    # Create three triangles sharing edges
    triangle1 = Triangle(0, [0, 1, 2], mesh_with_neighbors)
    triangle2 = Triangle(1, [1, 2, 3], mesh_with_neighbors)
    triangle3 = Triangle(2, [2, 3, 0], mesh_with_neighbors)
    
    mesh_with_neighbors.cells.extend([triangle1, triangle2, triangle3])
    
    # Store neighbors for all triangles
    for triangle in mesh_with_neighbors.cells:
        triangle.store_neighbours_and_edges()
    
    # Verify neighbor relationships
    assert len(triangle1._neighbours) == 2
    assert len(triangle2._neighbours) == 2
    assert len(triangle3._neighbours) == 2

def test_neighbor_edge_vectors(mesh_with_neighbors):
    """Test if edge vectors are correctly calculated for neighboring triangles."""
    # Create two adjacent triangles
    triangle1 = Triangle(0, [0, 1, 2], mesh_with_neighbors)
    triangle2 = Triangle(1, [1, 2, 3], mesh_with_neighbors)
    
    mesh_with_neighbors.cells.extend([triangle1, triangle2])
    
    # Store neighbors and edges
    triangle1.store_neighbours_and_edges()
    triangle2.store_neighbours_and_edges()
    
    # Verify edge vectors
    assert len(triangle1._edge_vectors) > 0
    assert len(triangle2._edge_vectors) > 0
    
    # Edge vectors should be 2D
    for vector in triangle1._edge_vectors:
        assert len(vector) == 2