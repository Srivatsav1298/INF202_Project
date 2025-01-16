import matplotlib.pyplot as plt
import matplotlib.tri as tri
import imageio
import os

class Animation():
    def __init__(self, mesh=None, fps=24):
        self._mesh = mesh
        self._points = self._mesh.points
        self._x = [p.x for p in self._points]
        self._y = [p.y for p in self._points]
        self._frame_count = 0
        self._fps = fps
        self._output_dir = "frames"

        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir)        

    def render_frame(self, frame_index=None):
        from ..cell.triangle_cell import Triangle
        triangles = [cell.points for cell in self._mesh.cells if isinstance(cell, Triangle)]
    
        oil_amount = [cell.oil_amount for cell in self._mesh.cells if isinstance(cell, Triangle)]

        triang = tri.Triangulation(self._x, self._y, triangles)
        
        plt.tripcolor(triang, facecolors=oil_amount, cmap='viridis', edgecolors='k')
        plt.colorbar(label='Oil Amount')
        plt.title('Oil Spill Simulation')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.gca().set_aspect('equal')

        frame_path = os.path.join(self._output_dir, f'frame_{frame_index:04d}.png')
        plt.savefig(frame_path)  # Save the frame as a PNG file
        plt.close()
        
        self._frame_count += 1

    def create_gif(self, gif_filename='/Users/ismasohail/Desktop/INF-Project/INF202_Project/OilSimulateProject/animation.gif'):
        frames = sorted([os.path.join(self._output_dir, f) for f in os.listdir(self._output_dir) if f.endswith('.png')])
        images = [imageio.imread(frame) for frame in frames]
        imageio.mimsave(gif_filename, images, fps=self._fps)
