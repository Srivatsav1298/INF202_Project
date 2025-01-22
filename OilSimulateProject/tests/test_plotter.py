import pytest
from unittest.mock import MagicMock
from pathlib import Path
from PIL import Image
from src.visualization.plotter import Animation

# Fixtures
@pytest.fixture
def mock_mesh():
    """Fixture to create a mock mesh object with valid triangles."""
    mock = MagicMock()
    mock.points = [
        MagicMock(x=0.1, y=0.2),
        MagicMock(x=0.3, y=0.4),
        MagicMock(x=0.5, y=0.6),
    ]
    mock.cells = [
        MagicMock(points=[0, 1, 2], oil_amount=0.5),
    ]
    return mock

@pytest.fixture
def animation_instance(mock_mesh, tmp_path):
    """Fixture to create an instance of Animation class."""
    return Animation(
        mesh=mock_mesh,
        fps=24,
        fishing_grounds=[[0.0, 0.5], [0.0, 0.5]],
        results_folder=tmp_path
    )

# Unit Tests
def test_initialization(animation_instance):
    """Test the initialization of the Animation class."""
    assert animation_instance._fps == 24
    assert animation_instance._x_min == 0.0
    assert animation_instance._y_max == 0.5
    assert isinstance(animation_instance._results_folder, Path)

def test_render_frame(animation_instance):
    """Test rendering a single frame."""
    animation_instance.render_frame(time_val=1.0, total_oil=0.5)

    assert len(animation_instance._frames) == 1
    assert isinstance(animation_instance._frames[0], Image.Image)

def test_make_plot(animation_instance, tmp_path):
    """Test creating and saving a plot to a file."""
    output_file = tmp_path / "result.png"

    animation_instance.make_plot(time_val=1.0, total_oil=0.5)

    assert output_file.exists(), "Plot file was not created."

def test_create_gif(animation_instance):
    """Test creating a GIF from frames."""
    # Add mock frames
    mock_frame = Image.new("RGB", (100, 100))
    animation_instance._frames = [mock_frame, mock_frame]

    animation_instance.create_gif()

    gif_file = animation_instance._results_folder / "animation.gif"
    assert gif_file.exists(), "GIF file was not created."

def test_invalid_mesh():
    """Test behavior when mesh is None."""
    with pytest.raises(ValueError, match="Mesh cannot be None"):
        Animation(mesh=None)

def test_render_frame_no_triangles(animation_instance):
    """Test rendering a frame with no triangles in the mesh."""
    animation_instance._mesh.cells = []  # No triangles

    with pytest.raises(ValueError, match="No triangles in mesh"):
        animation_instance.render_frame()

def test_make_plot_error_handling(animation_instance):
    """Test error handling when saving a plot fails."""
    animation_instance._results_folder = Path("/invalid/path")

    with pytest.raises(Exception):
        animation_instance.make_plot(time_val=1.0, total_oil=0.5)
