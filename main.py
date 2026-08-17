import numpy as np
import pyvista as pv
from moon_model import MoonModel

class LunarTrackApp:
    def __init__(self):
        # 1. Main 3D Plotter initialization
        self.plotter = pv.Plotter()
        self.plotter.title = "Lunar Track - 3D Interactive Viewer"
        
        # Pure Black Background for Space
        self.plotter.set_background('black')

        # Moon object initialize (Radius = 100)
        self.moon = MoonModel(radius=100.0)

    def setup_starfield_background(self):
        """Creates 3D Stars particle cloud background."""
        np.random.seed(42)
        num_stars = 3500

        radii = np.random.uniform(600, 2000, num_stars)
        theta = np.random.uniform(0, 2 * np.pi, num_stars)
        phi = np.random.uniform(0, np.pi, num_stars)

        x = radii * np.sin(phi) * np.cos(theta)
        y = radii * np.sin(phi) * np.sin(theta)
        z = radii * np.cos(phi)

        star_points = np.column_stack((x, y, z))
        star_cloud = pv.PolyData(star_points)

        self.plotter.add_mesh(
            star_cloud,
            color='white',
            point_size=1.5,
            render_points_as_spheres=True,
            lighting=False
        )

    def lock_zoom_and_setup_camera(self):
        """
        Sets camera interaction style.
        Allows 360-degree horizontal rotation around the moon, 
        and restricts ONLY vertical pitch (up/down) to prevent flipping.
        """
        # Initial Camera Position (Facing Near-side directly)
        self.plotter.camera.position = (0, -400, 0)
        self.plotter.camera.focal_point = (0, 0, 0)
        self.plotter.camera.up = (0, 0, 1)

        # PyVista terrain style keeps the Z-axis up vector locked
        self.plotter.enable_terrain_style()

        # 1. Disable Zooming/Scrolling
        def block_zoom_event(obj, event):
            return

        self.plotter.iren.add_observer("MouseWheelForwardEvent", block_zoom_event)
        self.plotter.iren.add_observer("MouseWheelBackwardEvent", block_zoom_event)
        self.plotter.iren.add_observer("RightButtonPressEvent", block_zoom_event)

        # 2. Lock ONLY Vertical Pitch (Up / Down polar limits)
        def constrain_vertical_pitch_event(obj, event):
            pos = np.array(self.plotter.camera.position)
            focal = np.array(self.plotter.camera.focal_point)
            vec = pos - focal
            r = np.linalg.norm(vec)
            
            if r == 0:
                return

            x, y, z = vec

            # Vertical pitch angle (elevation from equator plane)
            sin_phi = np.clip(z / r, -1.0, 1.0)
            phi = np.arcsin(sin_phi)

            # Limit vertical angle to +/- 80 degrees (prevents camera flipping at poles)
            max_elevation = np.radians(80.0)
            clamped_phi = np.clip(phi, -max_elevation, max_elevation)

            # If vertical pitch exceeds limit, correct Z and XY elevation without affecting 360 horizontal yaw
            if phi != clamped_phi:
                theta = np.arctan2(x, y)
                r_xy = r * np.cos(clamped_phi)
                
                new_x = r_xy * np.sin(theta)
                new_y = r_xy * np.cos(theta)
                new_z = r * np.sin(clamped_phi)

                self.plotter.camera.position = (new_x, new_y, new_z)
                self.plotter.camera.up = (0, 0, 1)
                self.plotter.render()

        # Observe user mouse drag interaction
        self.plotter.iren.add_observer("InteractionEvent", constrain_vertical_pitch_event)

    def run(self, mode="standard"):
        """
        Launches the complete 3D scene.
        :param mode: "standard" for normal texture, "topography" for elevation map
        """
        # Step 1: Background Starfield setup
        self.setup_starfield_background()

        # Step 2: Render Central 3D Moon
        self.moon.add_to_plotter(self.plotter, mode=mode)

        # Step 3: Camera, Zoom lock & Pitch limits
        self.lock_zoom_and_setup_camera()

        # Hide coordinate axes indicator
        self.plotter.hide_axes()

        print(f"Running Lunar Track in '{mode}' view mode...")
        self.plotter.show()


if __name__ == "__main__":
    app = LunarTrackApp()
    
    # Modes: "standard" or "topography"
    app.run(mode="standard")