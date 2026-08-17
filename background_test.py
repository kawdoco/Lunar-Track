import numpy as np
import pyvista as pv

def create_starfield_space():
    plotter = pv.Plotter()
    plotter.title = "Lunar Track - 3D Inside Space View (Zoom Locked)"

    # 1. Deep Space Pure Black Background
    plotter.set_background('black')

    # 2. Stars Cloud Generation
    np.random.seed(42)
    num_stars = 3000

    # Distance range: 500 idan 2000 venuruva
    radii = np.random.uniform(500, 2000, num_stars)
    theta = np.random.uniform(0, 2 * np.pi, num_stars)
    phi = np.random.uniform(0, np.pi, num_stars)

    x = radii * np.sin(phi) * np.cos(theta)
    y = radii * np.sin(phi) * np.sin(theta)
    z = radii * np.cos(phi)

    star_points = np.column_stack((x, y, z))
    star_cloud = pv.PolyData(star_points)

    # 3. Add Stars Mesh
    plotter.add_mesh(
        star_cloud,
        color='white',
        point_size=1.5,
        render_points_as_spheres=True,
        lighting=False
    )

    # 4. Camera Position Inside Center
    plotter.camera.position = (0, 0, 0.1)
    plotter.camera.focal_point = (0, 0, 1.0)
    plotter.camera.up = (0, 1, 0)

    # Trackball Style Enable Kirima
    plotter.enable_trackball_style()

    # 5. ZOOM DISABLE KIRIMA (Mouse Scroll Block Functionality)
    def block_zoom_event(obj, event):
        return

    plotter.iren.add_observer("MouseWheelForwardEvent", block_zoom_event)
    plotter.iren.add_observer("MouseWheelBackwardEvent", block_zoom_event)
    plotter.iren.add_observer("RightButtonPressEvent", block_zoom_event)

    plotter.hide_axes()
    print("Starfield Space Background (Zoom Locked) ready!")
    plotter.show()

if __name__ == "__main__":
    create_starfield_space()