import io
import matplotlib.pyplot as plt
import matplotlib.tri as tri
import matplotlib.patches as patches
import os
from PIL import Image

class Animation:
    def __init__(self, mesh=None, fps=24, fishing_grounds=[[0.0, 0.0], [0.0, 0.0]],output_dir="frames"):
        self._mesh = mesh
        self._points = self._mesh.points
        self._x = [p.x for p in self._points]
        self._y = [p.y for p in self._points]
        self._x_min, self._x_max = fishing_grounds[0]
        self._y_min, self._y_max = fishing_grounds[1]
        self._frame_count = 0
        self._fps = fps
        self._frames = []  # in-memory frames
        self._output_dir = output_dir
        
        # Create frames directory if it does not exist
        os.makedirs(self._output_dir, exist_ok=True)
        

    def render_frame(self, frame_index=None, time_val=0.0, total_oil=0.0):
        """
        Renders a single frame as a .png in a folder and appends it to the list of frames.
        """
        from ..cell.triangle_cell import Triangle

        # Collect triangle connectivity and oil amounts
        triangles = [cell.points for cell in self._mesh.cells if isinstance(cell, Triangle)]
        oil_amount = [cell.oil_amount for cell in self._mesh.cells if isinstance(cell, Triangle)]

        # Create the triangulation
        triang = tri.Triangulation(self._x, self._y, triangles)

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

        # Add time and total oil to the plot title
        ax.set_title(
            "Oil Spill Simulation\n"
            f"Time = {time_val:.2f} | Oil in Fishing Grounds = {total_oil:.2f}"
        )

        ax.add_patch(fishing_rectangle)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_aspect('equal')

        # Save the frame as a PNG file in the output directory
        frame_filename = os.path.join(self._output_dir, f"frame_{frame_index:04d}.png")
        plt.savefig(frame_filename, bbox_inches='tight')
        plt.close(fig)

        # Append to in-memory frames for GIF creation
        image = Image.open(frame_filename)
        self._frames.append(image)
        self._frame_count += 1

    def create_gif(self, gif_filename='animation.gif'):
        """
        Creates a GIF from the in-memory list of frames.
        The first frame is used as the 'base' frame, and the rest are appended.
        """
        if not self._frames:
            print("\n\nNo frames to create GIF.")
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

        print(f"\n\nGIF saved as {gif_filename}")
