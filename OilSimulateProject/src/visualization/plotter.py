import matplotlib.pyplot as plt
import matplotlib.tri as tri

def plot_mesh(mesh):
    from ..cell.triangle_cell import Triangle
    points = mesh.points

    x = [p.x for p in points]
    y = [p.y for p in points]

    triangles = [cell.points for cell in mesh.cells if isinstance(cell, Triangle)]
  
    intensity = [cell.oil_intensity for cell in mesh.cells if isinstance(cell, Triangle)]

    triang = tri.Triangulation(x, y, triangles)
    
    plt.tripcolor(triang, facecolors=intensity, cmap='viridis', edgecolors='k')
    plt.colorbar(label='Intensity')
    plt.title('2D Computational Mesh with Triangle-Specific Intensity')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.gca().set_aspect('equal')
    plt.show()
