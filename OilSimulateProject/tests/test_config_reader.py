import pytest
import os
import tomllib
from typing import Dict
import tempfile

from src.io.config_reader import (
    read_toml_file,
    validate_and_fill_defaults,
    load_single_config_file,
    load_all_configs_in_folder,
    REQUIRED_TOP_LEVEL_KEYS,
    REQUIRED_SETTINGS_KEYS,
    REQUIRED_GEOMETRY_KEYS
)

# Fixtures for creating test TOML files
@pytest.fixture
def valid_toml_content() -> str:
    """Fixture providing a valid TOML configuration."""
    return """
    [settings]
    nSteps = 100
    tStart = 0
    tEnd = 10

    [geometry]
    meshName = "test_mesh.msh"
    oilSpillCenter = [0.5, 0.5]
    borders = [[0, 1], [0, 1]]

    [IO]
    logName = "test_log"
    """

@pytest.fixture
def create_toml_file(valid_toml_content):
    """Fixture to create a temporary TOML file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as temp_file:
        temp_file.write(valid_toml_content)
        temp_file.close()
        yield temp_file.name
    os.unlink(temp_file.name)

# Test read_toml_file function
def test_read_toml_file_success(create_toml_file):
    """Test successful TOML file reading."""
    config = read_toml_file(create_toml_file)
    assert isinstance(config, dict)
    assert "settings" in config
    assert "geometry" in config

def test_read_toml_file_not_found():
    """Test error handling for non-existent file."""
    with pytest.raises(FileNotFoundError):
        read_toml_file("/path/to/nonexistent/file.toml")

def test_read_toml_file_invalid_syntax():
    """Test error handling for invalid TOML syntax."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as temp_file:
        temp_file.write("invalid toml syntax")
        temp_file.close()
        
        with pytest.raises(ValueError):
            read_toml_file(temp_file.name)
        
        os.unlink(temp_file.name)

# Test validate_and_fill_defaults function
@pytest.mark.parametrize("missing_section", REQUIRED_TOP_LEVEL_KEYS)
def test_validate_missing_top_level_sections(missing_section):
    """Test validation of missing top-level sections."""
    config = {
        section: {} for section in REQUIRED_TOP_LEVEL_KEYS if section != missing_section
    }
    
    with pytest.raises(ValueError, match=f"Missing top-level section '{missing_section}'"):
        validate_and_fill_defaults(config, "test.toml")

@pytest.mark.parametrize("missing_key", REQUIRED_SETTINGS_KEYS)
def test_validate_missing_settings_keys(missing_key):
    """Test validation of missing settings keys."""
    config = {
        "settings": {key: 10 for key in REQUIRED_SETTINGS_KEYS if key != missing_key},
        "geometry": {
            "meshName": "test.msh",
            "oilSpillCenter": [0.5, 0.5],
            "borders": [[0, 1], [0, 1]]
        }
    }
    
    with pytest.raises(ValueError, match=f"Missing required 'settings.{missing_key}'"):
        validate_and_fill_defaults(config, "test.toml")

@pytest.mark.parametrize("missing_key", REQUIRED_GEOMETRY_KEYS)
def test_validate_missing_geometry_keys(missing_key):
    """Test validation of missing geometry keys."""
    config = {
        "settings": {
            "nSteps": 100,
            "tEnd": 10
        },
        "geometry": {key: "test" for key in REQUIRED_GEOMETRY_KEYS if key != missing_key}
    }
    
    with pytest.raises(ValueError, match=f"Missing required 'geometry.{missing_key}'"):
        validate_and_fill_defaults(config, "test.toml")

def test_validate_restart_file_consistency(create_toml_file):
    """Test validation of restart file and tStart consistency."""
    config = read_toml_file(create_toml_file)
    
    # Test with restart file but tStart = 0
    config['IO']['restartFile'] = 'restart.txt'
    with pytest.raises(ValueError, match="Config test.toml specifies 'restartFile' but 'tStart' is 0"):
        validate_and_fill_defaults(config, "test.toml")

# Test load_single_config_file function
def test_load_single_config_file_success(create_toml_file):
    """Test successful loading of a single config file."""
    config = load_single_config_file(create_toml_file)
    assert isinstance(config, dict)
    assert "settings" in config
    assert "geometry" in config
    assert "IO" in config

# Test load_all_configs_in_folder function
def test_load_all_configs_in_folder(tmp_path):
    """Test loading multiple config files from a folder."""
    # Create multiple TOML files
    for i in range(3):
        with open(tmp_path / f"config{i}.toml", 'w') as f:
            f.write("""
            [settings]
            nSteps = 100
            tEnd = 10
            
            [geometry]
            meshName = "mesh.msh"
            oilSpillCenter = [0.5, 0.5]
            borders = [[0, 1], [0, 1]]
            """)
    
    configs = load_all_configs_in_folder(str(tmp_path))
    assert len(configs) == 3
    assert all('settings' in config for config in configs.values())

def test_load_all_configs_in_nonexistent_folder():
    """Test error handling for non-existent folder."""
    with pytest.raises(FileNotFoundError):
        load_all_configs_in_folder("/path/to/nonexistent/folder")

def test_load_all_configs_in_empty_folder(tmp_path):
    """Test error handling for folder with no TOML files."""
    with pytest.raises(FileNotFoundError):
        load_all_configs_in_folder(str(tmp_path))
