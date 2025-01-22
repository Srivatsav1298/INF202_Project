import pytest
import numpy as np
from unittest import mock
from unittest.mock import MagicMock, Mock, patch
from src.simulation.simulator import Simulation
from src.cell.triangle_cell import Triangle
import os

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
def test_simulation_initialization_with_boundary_conditions(mesh, nSteps, tStart, tEnd, should_raise, error_msg, tmp_path):
    solutions_dir = tmp_path / "solutions"
    solutions_dir.mkdir(parents=True)
    restart_file = solutions_dir / "input_solution.txt"
    restart_file.touch()

    if should_raise:
        with pytest.raises(ValueError) as exc_info:
            Simulation(
                mesh, (0, 0), ((0, 10), (0, 10)), nSteps, tStart, tEnd, 30, str(tmp_path), str(restart_file), "input"
            )
        assert str(exc_info.value) == error_msg
    else:
        simulation = Simulation(
            mesh, (0, 0), ((0, 10), (0, 10)), nSteps, tStart, tEnd, 30, str(tmp_path), str(restart_file), "input"
        )
        assert simulation._nSteps == nSteps

@patch("builtins.open", mock.mock_open(read_data="mocked data"))
def test_oil_movement(mock_mesh, tmp_path):
    mock_cell = MagicMock(spec=Triangle)
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
    
    solutions_dir = tmp_path / "solutions"
    solutions_dir.mkdir(parents=True)
    restart_file = solutions_dir / "input_solution.txt"
    restart_file.touch()
    
    sim = Simulation(mock_mesh, (0.0, 0.0), ((-5, 5), (-5, 5)), 10, 0.0, 10.0, 30, str(tmp_path), str(restart_file), "input")
    # Add assertions or further test logic here

@pytest.mark.parametrize(
    "cell_type, expected_called_method",
    [
        ('line', 'calculate_oil_amount'),
        ('boundary', 'calculate_oil_amount'),
    ]
)
def test_cell_oil_calculation(cell_type, expected_called_method, mock_mesh, tmp_path):
    cell = MagicMock()
    cell.type = cell_type
    mock_mesh.cells = [cell]
    
    solutions_dir = tmp_path / "solutions"
    solutions_dir.mkdir(parents=True)
    restart_file = solutions_dir / "input_solution.txt"
    restart_file.touch()
    
    with patch('os.path.isfile', return_value=True):
        simulation = Simulation(
            mock_mesh, (0, 0), ((0, 10), (0, 10)), 10, 0.0, 100.0, 30,
            str(tmp_path), str(restart_file), "input"
        )
        simulation.initialize_oil_spill()
    
    getattr(cell, expected_called_method).assert_called_once()

@pytest.mark.parametrize(
    "cell_type, should_calculate_oil",
    [
        ('line', True),
        ('boundary', True),
        ('other', False),
    ]
)
def test_cell_oil_calculation_for_different_types(cell_type, should_calculate_oil, mock_mesh, tmp_path):
    cell = MagicMock()
    cell.type = cell_type
    mock_mesh.cells = [cell]
    
    solutions_dir = tmp_path / "solutions"
    solutions_dir.mkdir(parents=True)
    restart_file = solutions_dir / "input_solution.txt"
    restart_file.touch()
    
    with patch('os.path.isfile', return_value=True):
        simulation = Simulation(
            mock_mesh, (0, 0), ((0, 10), (0, 10)), 10, 0.0, 100.0, 30,
            str(tmp_path), str(restart_file), "input"
        )
        simulation.initialize_oil_spill()
    
    if should_calculate_oil:
        cell.calculate_oil_amount.assert_called_once()
    else:
        cell.calculate_oil_amount.assert_not_called()

@pytest.mark.parametrize("cells, fishing_grounds, expected_oil", [
    ([Mock(midpoint=(0, 0), oil_amount=1.0)], ((-1, 1), (-1, 1)), 1.0),
    ([Mock(midpoint=(2, 2), oil_amount=1.0)], ((-1, 1), (-1, 1)), 0.0),
    ([Mock(midpoint=(0.5, 0.5), oil_amount=2.0)], ((0, 1), (0, 1)), 2.0),
])
def test_check_fishing_grounds(mock_mesh, cells, fishing_grounds, expected_oil, tmp_path):
    for cell in cells:
        cell.midpoint = cell.midpoint
        cell.oil_amount = cell.oil_amount
    
    mock_mesh.cells = cells
    
    solutions_dir = tmp_path / "solutions"
    solutions_dir.mkdir(parents=True)
    restart_file = solutions_dir / "input_solution.txt"
    restart_file.touch()
    
    sim = Simulation(mock_mesh, (0.0, 0.0), fishing_grounds, 10, 0.0, 10.0, 30, str(tmp_path), str(restart_file), "input")
    total_oil = sim.check_fishing_grounds(0)
    
    assert total_oil == pytest.approx(expected_oil)

@pytest.mark.parametrize("u_i, u_ngh, v_vector, v_avg, expected_flux", [
    (1.0, 0.5, np.array([1, 0]), np.array([0.5, 0]), 0.5),
    (1.0, 0.5, np.array([1, 0]), np.array([-0.5, 0]), 0.0),
])
def test_flux_function(u_i, u_ngh, v_vector, v_avg, expected_flux, mock_mesh, tmp_path):
    solutions_dir = tmp_path / "solutions"
    solutions_dir.mkdir(parents=True)
    restart_file = solutions_dir / "input_solution.txt"
    restart_file.touch()
    
    sim = Simulation(mock_mesh, (0.0, 0.0), ((-5, 5), (-5, 5)), 10, 0.0, 10.0, 30, str(tmp_path), str(restart_file), "input")
    
    flux = sim.g(u_i, u_ngh, v_vector, v_avg)
    
    assert flux == pytest.approx(expected_flux)
