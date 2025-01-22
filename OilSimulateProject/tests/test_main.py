import pytest
import logging
import argparse
from unittest.mock import patch, MagicMock, ANY
from main import setup_logging, run_simulation_for_config, main
from pathlib import Path

@pytest.fixture
def mock_config():
    return {
        "IO": {"logName": "test_log"},
        "settings": {"nSteps": 100, "tStart": 0, "tEnd": 10},
        "geometry": {
            "meshName": "test_mesh.msh",
            "oilSpillCenter": [0.5, 0.5],
            "borders": [[0, 1], [0, 1]]
        }
    }

def test_setup_logging():
    """Test if setup_logging creates a logger with correct configuration."""
    with patch('logging.FileHandler') as mock_file_handler:
        logger = setup_logging('test.log', logging.INFO)
        assert logger.level == logging.INFO
        mock_file_handler.assert_called_once_with('test.log', mode='w')

@patch('main.Mesh')
@patch('main.Simulation')
@patch('main.logging.getLogger')
def test_run_simulation_for_config(mock_get_logger, mock_simulation, mock_mesh, mock_config):
    """Test if run_simulation_for_config correctly sets up and runs a simulation."""
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    run_simulation_for_config(mock_config, 'test_config.toml')

    mock_logger.info.assert_called_with(ANY)
    mock_mesh.assert_called_once()
    mock_simulation.assert_called_once()
    mock_simulation.return_value.run_simulation.assert_called_once()

@patch('argparse.ArgumentParser.parse_args')
@patch('main.load_single_config_file')
@patch('main.run_simulation_for_config')
def test_main_single_config(mock_run_simulation, mock_load_config, mock_args):
    """Test if main function correctly handles a single configuration file."""
    mock_args.return_value = MagicMock(find=None, folder=None, config_file='test.toml')
    mock_load_config.return_value = {'test': 'config'}
    
    main()
    
    mock_load_config.assert_called_once_with('test.toml')
    mock_run_simulation.assert_called_once_with({'test': 'config'}, 'test.toml')

# Add more tests for other scenarios and edge cases@patch('argparse.ArgumentParser.parse_args')
def test_main_argument_parsing(mock_args):
    """Test command-line argument parsing in main function."""
    test_cases = [
        (argparse.Namespace(find=None, folder=None, config_file='custom.toml'), 'custom.toml'),
        (argparse.Namespace(find=None, folder=None, config_file=None), 'input.toml'),
        (argparse.Namespace(find='all', folder='custom_folder', config_file=None), 'custom_folder'),
    ]
    
    for args, expected in test_cases:
        mock_args.return_value = args
        with patch('main.load_single_config_file') as mock_load_single, \
             patch('main.load_all_configs_in_folder') as mock_load_all, \
             patch('main.run_simulation_for_config'):
            
            main()
            
            if args.find == 'all':
                mock_load_all.assert_called_once_with(expected)
            else:
                mock_load_single.assert_called_once_with(expected)

@patch('argparse.ArgumentParser.parse_args')
def test_main_argument_parsing(mock_args):
    """Test command-line argument parsing in main function."""
    test_cases = [
        (argparse.Namespace(find=None, folder=None, config_file='custom.toml'), 'custom.toml'),
        (argparse.Namespace(find=None, folder=None, config_file=None), 'config_files/input.toml'),
        (argparse.Namespace(find='all', folder='custom_folder', config_file=None), 'custom_folder'),
        (argparse.Namespace(find=None, folder='custom_folder', config_file='custom.toml'), 'custom_folder/custom.toml'),
    ]

    for args, expected in test_cases:
        mock_args.return_value = args
        with patch('main.load_single_config_file') as mock_load_single, \
             patch('main.load_all_configs_in_folder') as mock_load_all, \
             patch('main.run_simulation_for_config'):

            main()

            if args.find == 'all':
                mock_load_all.assert_called_once_with(expected)
            else:
                mock_load_single.assert_called_once_with(expected)
