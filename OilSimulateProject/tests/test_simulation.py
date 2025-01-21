import pytest
import numpy as np
from unittest.mock import Mock, patch
from src.simulation.simulator import Simulation
from src.visualization.plotter import Animation


@pytest.fixture
def mock_mesh():
    """
    Fixture to mock the mesh with cells.
    """
    mock_mesh = Mock()
    mock_mesh.cells = []  # Mock cells
    return mock_mesh


def test_simulation_init(mock_mesh):
    """
    Test the initialization of the Simulation object to ensure all attributes are properly set.
    """
    oil_spill_center = (0.0, 0.0)
    fishing_grounds = ((-5.0, 5.0), (-5.0, 5.0))
    n_steps = 10
    t_start = 0.0
    t_end = 10.0
    fps = 30
    results_folder = 'results/test_folder'
    
    sim = Simulation(mock_mesh, oil_spill_center, fishing_grounds, n_steps, t_start, t_end, fps, results_folder)
    
    assert sim._oil_spill_center == oil_spill_center
    assert sim._fishing_grounds == fishing_grounds
    assert sim._nSteps == n_steps
    assert sim._tStart == t_start
    assert sim._tEnd == t_end
    assert sim._fps == fps
    assert sim._results_folder == results_folder
    assert sim._delta_t == (t_end / n_steps)


@pytest.mark.parametrize("oil_spill_center, num_cells", [
    ((0.0, 0.0), 10),
    ((0.5, 0.5), 5),
])
def test_initialize_oil_spill(mock_mesh, oil_spill_center, num_cells):
    """
    Test if the oil spill is initialized correctly for all cells.
    """
    from src.cell.triangle_cell import Triangle
    
    # Create individual mock cells
    mock_cells = [Mock(spec=Triangle) for _ in range(num_cells)]
    for cell in mock_cells:
        cell.calculate_oil_amount = Mock()
    
    mock_mesh.cells = mock_cells  # Assign the mock cells to the mesh
    
    sim = Simulation(mock_mesh, oil_spill_center, ((-5, 5), (-5, 5)), 10, 0.0, 10.0, 30, "results/")
    sim.initialize_oil_spill()
    
    # Assert each cell's method was called exactly once
    for cell in mock_mesh.cells:
        cell.calculate_oil_amount.assert_called_once_with(oil_spill_center)


def test_oil_movement(mock_mesh):
    """
    Test the oil movement computation and ensure oil flux is calculated and applied correctly.
    """
    from src.cell.triangle_cell import Triangle
    
    mock_cell = Mock(spec=Triangle)
    mock_cell.neighbours = [Mock(spec=Triangle) for _ in range(3)]
    mock_cell.outward_normals = [np.array([1, 0]) for _ in range(3)]
    mock_cell.edge_vectors = [np.array([1, 0]) for _ in range(3)]
    mock_cell.velocity_field = [1.0, 0.0]
    mock_cell.area = 1.0
    mock_cell.oil_amount = 5.0
    mock_cell.update_oil_amount = Mock()
    
    for ngh in mock_cell.neighbours:
        ngh.velocity_field = [0.5, 0.0]
    
    mock_mesh.cells = [mock_cell]
    
    sim = Simulation(mock_mesh, (0.0, 0.0), ((-5, 5), (-5, 5)), 10, 0.0, 10.0, 30, "results/")
    sim.oil_movement()
    
    mock_cell.update_oil_amount.assert_called_once()  # Check update method is called


def test_render_simulation_step(mock_mesh):
    """
    Test that rendering simulation steps works correctly and generates expected frames.
    """
    mock_animation = Mock(spec=Animation)
    sim = Simulation(mock_mesh, (0.0, 0.0), ((-5, 5), (-5, 5)), 10, 0.0, 10.0, 30, "results/")
    current_time = sim._delta_t  # This matches the time calculation logic in render_simulation_step
    total_oil_in_fishing_grounds = 0  # Mock a value if needed

    with patch.object(sim, 'check_fishing_grounds', return_value=total_oil_in_fishing_grounds):
        sim.render_simulation_step(mock_animation, 1)
    
    mock_animation.render_frame.assert_called_once_with(2, current_time, total_oil_in_fishing_grounds)



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
        cell.midpoint = cell.midpoint
        cell.oil_amount = cell.oil_amount
    mock_mesh.cells = cells
    
    sim = Simulation(mock_mesh, (0.0, 0.0), fishing_grounds, 10, 0.0, 10.0, 30, "results/")
    total_oil = sim.check_fishing_grounds(0)
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
    mock_mesh.cells = []  # Ensure cells is iterable

    with patch('src.simulation.simulator.Simulation.initialize_oil_spill'):
        sim = Simulation(mock_mesh, (0.0, 0.0), ((-5, 5), (-5, 5)), 10, 0.0, 10.0, 30, "results/")
        flux = sim.g(u_i, u_ngh, v_vector, v_avg)
        assert flux == pytest.approx(expected_flux)
