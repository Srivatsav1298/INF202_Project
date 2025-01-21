import io
import matplotlib.pyplot as plt
import matplotlib.tri as tri
import matplotlib.patches as patches
from PIL import Image
from typing import List, Optional

class Animation:
    def __init__(self, mesh=None, fps: int = 24, fishing_grounds: List[List[float]] = [[0.0, 0.0], [0.0, 0.0]], results_folder=None):
        """
        Initializes the Animation class with mesh data, frame rate, fishing ground boundaries, and a results folder.

        :param mesh: The mesh object containing points and cells (default: None).
        :param fps: Frames per second for animations (default: 24).
        :param fishing_grounds: Coordinates for the fishing ground rectangle as [[x_min, x_max], [y_min, y_max]].
        :param results_folder: Folder to save rendered results (default: None).
        """
        self._mesh = mesh
        self._points = self._mesh.points if self._mesh else []
        self._x = [p.x for p in self._points]
        self._y = [p.y for p in self._points]
        self._x_min, self._x_max = fishing_grounds[0]
        self._y_min, self._y_max = fishing_grounds[1]
        self._frame_count = 0
        self._fps = fps
        self._results_folder = results_folder
        self._frames: List[Image.Image] = []  # Store frames in memory

    def render_frame(self, time_val: float = 0.0, total_oil: float = 0.0):
        """
        Renders a single frame as a Pillow Image and appends it to the in-memory list of frames.

        :param frame_index: Index of the current frame (optional).
        :param time_val: Current simulation time (default: 0.0).
        :param total_oil: Total oil within the fishing grounds at this time (default: 0.0).
        """
        from ..cell.triangle_cell import Triangle

        # Extract triangle connectivity and oil data
        triangles = [cell.points for cell in self._mesh.cells if isinstance(cell, Triangle)]
        oil_amount = [cell.oil_amount for cell in self._mesh.cells if isinstance(cell, Triangle)]

        # Generate the triangulation object
        triang = tri.Triangulation(self._x, self._y, triangles)

        # Calculate fishing rectangle dimensions
        width = self._x_max - self._x_min
        height = self._y_max - self._y_min

        fishing_rectangle = patches.Rectangle(
            (self._x_min, self._y_min),  # Bottom-left corner
            width,
            height,
            fill=False,
            edgecolor="red",
            linewidth=1
        )

        # Plot the current frame
        fig, ax = plt.subplots()
        tpc = ax.tripcolor(triang, facecolors=oil_amount, cmap='viridis', edgecolors='k', vmin=0, vmax=1)
        fig.colorbar(tpc, label='Oil Amount')

        # Add titles and labels
        ax.set_title(
            "Oil Spill Simulation\n"
            f"Time = {time_val:.2f} | Oil in Fishing Grounds = {total_oil:.2f}"
        )
        ax.add_patch(fishing_rectangle)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_aspect('equal')

        # Save the plot to a memory buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        plt.close(fig)

        # Convert buffer to Pillow image
        buffer.seek(0)
        image = Image.open(buffer)
        image.load()  # Load image into memory
        buffer.close()

        # Store the frame and update frame count
        self._frames.append(image)
        self._frame_count += 1

    def make_plot(self, time_val: float = 0.0, total_oil: float = 0.0):
        """
        Renders and saves a single frame to a file.

        :param filename: File path to save the frame (default: 'result.png').
        :param frame_index: Index of the frame to render (optional).
        :param time_val: Simulation time for the frame (default: 0.0).
        :param total_oil: Total oil in the fishing grounds (default: 0.0).
        """
        from ..cell.triangle_cell import Triangle

        # Default filename inside the results folder
        filename = self._results_folder / "result.png"

        # Extract triangle connectivity and oil data
        triangles = [cell.points for cell in self._mesh.cells if isinstance(cell, Triangle)]
        oil_amount = [cell.oil_amount for cell in self._mesh.cells if isinstance(cell, Triangle)]

        # Generate the triangulation object
        triang = tri.Triangulation(self._x, self._y, triangles)

        # Fishing grounds rectangle dimensions
        width = self._x_max - self._x_min
        height = self._y_max - self._y_min

        fishing_rectangle = patches.Rectangle(
            (self._x_min, self._y_min),
            width,
            height,
            fill=False,
            edgecolor="red",
            linewidth=1
        )

        # Plot the frame
        fig, ax = plt.subplots()
        tpc = ax.tripcolor(triang, facecolors=oil_amount, cmap='viridis', edgecolors='k', vmin=0, vmax=1)
        fig.colorbar(tpc, label='Oil Amount')

        # Add titles and labels
        ax.set_title(
            "Oil Spill Simulation\n"
            f"Time = {time_val:.2f} | Oil in Fishing Grounds = {total_oil:.2f}"
        )
        ax.add_patch(fishing_rectangle)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_aspect('equal')

        # Save the figure
        try:
            plt.savefig(filename, format='png', bbox_inches='tight')
            plt.close(fig)
            print(f"Last frame saved as {filename}")
        except Exception as e:
            print(f"Failed to save last frame: {e}")

    def create_gif(self):
        """
        Creates a GIF animation from the stored in-memory frames.

        Saves the GIF to the specified results folder.
        """
        gif_filename = self._results_folder / "animation.gif"

        if not self._frames:
            print("No frames to create GIF.")
            return

        # Use the first frame as the base for the GIF
        first_frame = self._frames[0]

        # Save all frames as a GIF
        first_frame.save(
            gif_filename,
            save_all=True,
            append_images=self._frames[1:],
            duration=1000 / self._fps,  # Milliseconds per frame
            loop=0
        )

        print(f"\nGIF saved as {gif_filename}")
