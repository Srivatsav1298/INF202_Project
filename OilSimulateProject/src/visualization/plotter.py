import io
import matplotlib.pyplot as plt
import matplotlib.tri as tri
import matplotlib.patches as patches
from PIL import Image

class Animation:
    def __init__(self, mesh=None, fps=24, fishing_grounds=[[0.0, 0.0], [0.0, 0.0]]):
        self._mesh = mesh
        self._points = self._mesh.points
        self._x = [p.x for p in self._points]
        self._y = [p.y for p in self._points]
        self._x_min, self._x_max = fishing_grounds[0]
        self._y_min, self._y_max = fishing_grounds[1]
        self._frame_count = 0
        self._fps = fps
        self._frames = []  # in-memory frames

    def render_frame(self, frame_index=None, time_val=0.0, total_oil=0.0):
        """
        Renders a single frame in-memory as a Pillow Image
        and appends it to the list of frames.
        
        :param frame_index: An integer index for the frame.
        :param time_val: The current simulation time (float).
        :param total_oil: Total oil in fishing grounds at this time (float).
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
            (self._x_min, self._y_min), #bottomleft corner
            width,
            height,
            fill = False,
            edgecolor = "red",
            linewidth = 1
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

        # Save this figure to an in-memory buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        plt.close(fig)

        # Rewind buffer, open in Pillow
        buffer.seek(0)
        image = Image.open(buffer)
        image.load()   # force-load into memory
        buffer.close() # now safe to close buffer

        self._frames.append(image)
        self._frame_count += 1

    def make_plot(self, filename='result.png', frame_index=None, time_val=0.0, total_oil=0.0):
        """
        Renders and saves a single frame directly to a file.
        
        :param filename: The filename for saving the image (default: 'last_frame.png').
        :param frame_index: The frame index to render (optional).
        :param time_val: The time value for the frame (float, optional).
        :param total_oil: The total oil amount for the frame (float, optional).
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
            (self._x_min, self._y_min),  # bottom-left corner
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

        # Save directly to the specified filename
        try:
            plt.savefig(filename, format='png', bbox_inches='tight')
            plt.close(fig)
            print(f"\n\nLast frame saved as {filename}")
        except Exception as e:
            print(f"\n\nFailed to save last frame: {e}")


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
