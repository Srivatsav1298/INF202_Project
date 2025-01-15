import matplotlib.pyplot as plt
import matplotlib.tri as tri
<<<<<<< HEAD
import matplotlib.animation as animation
import numpy as np

def plot_mesh(mesh):
    """Static plot of the mesh with current oil intensity"""
    from ..cell.triangle_cell import Triangle
    
    points = mesh.points
    x = [p.x for p in points]
    y = [p.y for p in points]
    triangles = [cell.points for cell in mesh.cells if isinstance(cell, Triangle)]
    intensity = [cell.oil_intensity for cell in mesh.cells if isinstance(cell, Triangle)]
    
    triang = tri.Triangulation(x, y, triangles)
    plt.figure(figsize=(10, 8))
    plt.tripcolor(triang, facecolors=intensity, cmap='viridis', edgecolors='k')
    plt.colorbar(label='Oil Intensity')
    plt.title('Oil Distribution')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.gca().set_aspect('equal')
    plt.show()

def create_animation(simulation, num_frames=100):
    """Create an animation of the oil flow"""
    from ..cell.triangle_cell import Triangle
    
    # Setup the figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Get mesh data
    mesh = simulation._mesh
    points = mesh.points
    x = [p.x for p in points]
    y = [p.y for p in points]
    triangles = [cell.points for cell in mesh.cells if isinstance(cell, Triangle)]
    triang = tri.Triangulation(x, y, triangles)
    
    # Plot fishing grounds
    fishing_grounds = plt.Rectangle((0.0, 0.0), 0.45, 0.2, 
                                  fill=False, color='red', 
                                  linestyle='--', label='Fishing Grounds')
    ax.add_patch(fishing_grounds)
    
    # Time step for each frame
    dt = simulation._end_time / num_frames
    simulation._dt = dt  # Update simulation time step
    
    # Initialize plot
    intensity = [cell.oil_intensity for cell in mesh.cells if isinstance(cell, Triangle)]
    plot = ax.tripcolor(triang, facecolors=intensity, cmap='viridis', edgecolors='k')
    plt.colorbar(plot, label='Oil Intensity')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_aspect('equal')
    ax.legend()
    
    def update(frame):
        """Update function for animation"""
        simulation.step()
        intensity = [cell.oil_intensity for cell in mesh.cells if isinstance(cell, Triangle)]
        plot.set_array(np.array(intensity))
        ax.set_title(f'Time: {simulation._current_time:.2f}')
        return plot,
    
    # Create animation
    anim = animation.FuncAnimation(fig, update, frames=num_frames, 
                                 interval=50, blit=True)
    
    # Save animation
    anim.save('oil_flow.gif', writer='pillow')
    plt.show()
=======
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

    def create_gif(self, gif_filename='animation.gif'):
        frames = sorted([os.path.join(self._output_dir, f) for f in os.listdir(self._output_dir) if f.endswith('.png')])
        images = [imageio.imread(frame) for frame in frames]
        imageio.mimsave(gif_filename, images, fps=self._fps)
>>>>>>> origin/main
