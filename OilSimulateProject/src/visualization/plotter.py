import matplotlib.pyplot as plt
import matplotlib.tri as tri
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