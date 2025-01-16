# plotter.py

import io
import matplotlib.pyplot as plt
import matplotlib.tri as tri
from PIL import Image

class Animation:
    def __init__(self, mesh=None, fps=24):
        self._mesh = mesh
        self._points = self._mesh.points
        self._x = [p.x for p in self._points]
        self._y = [p.y for p in self._points]
        self._frame_count = 0
        self._fps = fps
        self._frames = []  # Store frames in-memory

    def render_frame(self, frame_index=None):
        """
        Renders a single frame in-memory as a Pillow Image
        and appends it to the list of frames.
        """
        from ..cell.triangle_cell import Triangle

        # Collect triangle connectivity and oil amounts
        triangles = [cell.points for cell in self._mesh.cells if isinstance(cell, Triangle)]
        oil_amount = [cell.oil_amount for cell in self._mesh.cells if isinstance(cell, Triangle)]

        # Create the triangulation
        triang = tri.Triangulation(self._x, self._y, triangles)

        # Plot the frame
        fig, ax = plt.subplots()
        tpc = ax.tripcolor(triang, facecolors=oil_amount, cmap='viridis', edgecolors='k')
        fig.colorbar(tpc, label='Oil Amount')

        ax.set_title('Oil Spill Simulation')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_aspect('equal')

        # Save this figure to an in-memory buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        plt.close(fig)

        # Rewind buffer, open in Pillow
        buffer.seek(0)
        image = Image.open(buffer)

        # Force-load the image data into memory now
        # so it doesn't rely on the buffer later.
        image.load()

        # You can now safely close the buffer
        buffer.close()

        # Add the loaded image to frames
        self._frames.append(image)

        self._frame_count += 1

    def create_gif(self, gif_filename='animation.gif'):
        """
        Creates a GIF from the in-memory list of frames.
        The first frame is used as the "base" frame, and the rest are appended.
        """
        if not self._frames:
            print("No frames to create GIF.")
            return

        # Use the first frame as the base
        first_frame = self._frames[0]

        # Save all frames as a GIF
        first_frame.save(
            gif_filename,
            save_all=True,
            append_images=self._frames[1:],  # Remainder of frames
            duration=1000 / self._fps,       # ms per frame
            loop=0
        )

        print(f"GIF saved as {gif_filename}")
