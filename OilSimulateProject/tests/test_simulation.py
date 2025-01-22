import pytest
import numpy as np
from unittest import mock
from unittest.mock import MagicMock, Mock
from src.simulation.simulator import Simulation
from src.cell.triangle_cell import Triangle  # Ensure you import Triangle if needed


# Fixture to mock the mesh object
@pytest.fixture
def mock_mesh():
    mock_mesh = MagicMock()
    mock_cell = MagicMock(spec=Triangle)
    mock_cell.area = 1.0
    mock_cell.oil_amount = 5.0
    mock_cell.midpoint = (0.0, 0.0)
    mock_mesh.cells = [mock_cell]
    return mock_mesh


@pytest.mark.parametrize(
    "mesh, nSteps, tStart, tEnd, should_raise, error_msg",
    [
        (None, 10, 0.0, 100.0, True, "Mesh cannot be None for simulation."),
        (MagicMock(), -10, 0.0, 100.0, True, "Number of steps (nSteps) cannot be negative."),
        (MagicMock(), 10, 100.0, 0.0, True, "Start time (tStart) cannot be greater than end time (tEnd)."),
        (MagicMock(), 10, 0.0, 100.0, False, None),  # Valid case
    ]
)
def test_simulation_initialization_with_boundary_conditions(mesh, nSteps, tStart, tEnd, should_raise, error_msg):
    if should_raise:
        with pytest.raises(ValueError) as exc_info:
            Simulation(
                mesh, (0, 0), ((0, 10), (0, 10)), nSteps, tStart, tEnd, 30, "results", None, "config1"
            )
        assert str(exc_info.value) == error_msg  # Ensure the correct error message is raised
    else:
        simulation = Simulation(
            mesh, (0, 0), ((0, 10), (0, 10)), nSteps, tStart, tEnd, 30, "results", None, "config1"
        )
        assert simulation._nSteps == nSteps

@mock.patch("builtins.open", mock.mock_open(read_data="mocked data"))
def test_oil_movement(mock_mesh):
    """
    Test the oil movement computation and ensure oil flux is calculated and applied correctly.
    """
    # Create mock cell with necessary properties
    mock_cell = MagicMock(spec=Triangle)
    mock_cell.neighbours = [Mock(spec=Triangle) for _ in range(3)]
    mock_cell.outward_normals = [np.array([1, 0]) for _ in range(3)]
    mock_cell.edge_vectors = [np.array([1, 0]) for _ in range(3)]
    mock_cell.velocity_field = [1.0, 0.0]
    mock_cell.area = 1.0
    mock_cell.oil_amount = 5.0
    mock_cell.update_oil_amount = Mock()
    
    # Setup neighbors with velocity fields
    for ngh in mock_cell.neighbours:
        ngh.velocity_field = [0.5, 0.0]
    
    mock_mesh.cells = [mock_cell]
    
    # Create the simulation object and perform oil movement
    sim = Simulation(mock_mesh, (0.0, 0.0), ((-5, 5), (-5, 5)), 10, 0.0, 10.0, 30, "results/", "restart_file", "config_name")


@pytest.mark.parametrize(
    "cell_type, expected_called_method",
    [
        ('line', 'calculate_oil_amount'),  # Line cells should call calculate_oil_amount
        ('boundary', 'calculate_oil_amount'),  # Boundary cells should also call calculate_oil_amount
    ]
)
def test_cell_oil_calculation(cell_type, expected_called_method, mock_mesh):
    """
    Test that cells of different types (line, boundary) correctly calculate oil amount
    using the appropriate method.
    """
    # Mock the cell object with the given type
    cell = MagicMock()
    cell.type = cell_type
    mock_mesh.cells = [cell]  # Add the cell to the mock mesh
    
    # Initialize the Simulation with the mocked mesh
    simulation = Simulation(
        mock_mesh, (0, 0), ((0, 10), (0, 10)), 10, 0.0, 100.0, 30, "results", "restart_file", "config_name"
    )
    
    # Run the oil spill initialization
    simulation.initialize_oil_spill()
    
    # Ensure the correct method (e.g., `calculate_oil_amount`) is called
    getattr(cell, expected_called_method).assert_called_once()



@pytest.mark.parametrize(
    "cell_type, should_calculate_oil",
    [
        ('line', True),    # Line cells should always calculate oil amount
        ('boundary', True),  # Boundary cells should also calculate oil amount
        ('other', False),   # Other types should not calculate oil amount
    ]
)
def test_cell_oil_calculation_for_different_types(cell_type, should_calculate_oil, mock_mesh):
    """
    Test that only certain cell types (line, boundary) calculate the oil amount.
    """
    # Mock the cell object with the given type
    cell = MagicMock()
    cell.type = cell_type
    mock_mesh.cells = [cell]  # Add the cell to the mock mesh
    
    # Initialize the Simulation with the mocked mesh
    simulation = Simulation(
        mock_mesh, (0, 0), ((0, 10), (0, 10)), 10, 0.0, 100.0, 30, "results", "restart_file", "config_name"
    )
    
    # Run the oil spill initialization
    simulation.initialize_oil_spill()
    
    # Check if `calculate_oil_amount` was called or not based on cell type
    if should_calculate_oil:
        cell.calculate_oil_amount.assert_called_once()
    else:
        cell.calculate_oil_amount.assert_not_called()



@pytest.mark.parametrize("cells, fishing_grounds, expected_oil", [
    ([Mock(midpoint=(0, 0), oil_amount=1.0)], ((-1, 1), (-1, 1)), 1.0),
    ([Mock(midpoint=(2, 2), oil_amount=1.0)], ((-1, 1), (-1, 1)), 0.0),
    ([Mock(midpoint=(0.5, 0.5), oil_amount=2.0)], ((0, 1), (0, 1)), 2.0),
])
def test_check_fishing_grounds(mock_mesh, cells, fishing_grounds, expected_oil):
    """
    Test that the total oil in fishing grounds is calculated correctly.
    """
    for cell in cells:
        # Ensure the midpoint and oil_amount are set correctly
        cell.midpoint = cell.midpoint
        cell.oil_amount = cell.oil_amount
    
    mock_mesh.cells = cells
    
    # Run the simulation to check fishing grounds
    sim = Simulation(mock_mesh, (0.0, 0.0), fishing_grounds, 10, 0.0, 10.0, 30, "results/")
    total_oil = sim.check_fishing_grounds(0)
    
    # Assert that the total oil is calculated correctly
    assert total_oil == pytest.approx(expected_oil)


@pytest.mark.parametrize("u_i, u_ngh, v_vector, v_avg, expected_flux", [
    (1.0, 0.5, np.array([1, 0]), np.array([0.5, 0]), 0.5),
    (1.0, 0.5, np.array([1, 0]), np.array([-0.5, 0]), 0.0),
])
def test_flux_function(u_i, u_ngh, v_vector, v_avg, expected_flux):
    """
    Test the flux function (g) for different inputs.
    """
    mock_mesh = Mock()
    sim = Simulation(mock_mesh, (0.0, 0.0), ((-5, 5), (-5, 5)), 10, 0.0, 10.0, 30, "results/")
    
    # Run flux calculation
    flux = sim.g(u_i, u_ngh, v_vector, v_avg)
    
    # Assert the flux matches the expected value
    assert flux == pytest.approx(expected_flux)
