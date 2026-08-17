import os
import pyvista as pv

class MoonModel:
    def __init__(self, radius=100.0):
        """
        3D Moon Model Component aligned with NASA Lunar Near-Side mapping.
        :param radius: Moon spherical mesh scale size
        """
        self.radius = radius
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Image file paths setup
        self.texture_path = os.path.join(self.script_dir, "assets", "moon.jpg")
        self.topography_path = os.path.join(self.script_dir, "assets", "topography.jpg")
        
        self.mesh = None
        self.actor = None

    def build_mesh(self):
        """
        Create high-density sphere and align Near-Side to front facing camera.
        """
        raw_sphere = pv.Sphere(
            radius=self.radius, 
            theta_resolution=360, 
            phi_resolution=180
        )
        self.mesh = raw_sphere.texture_map_to_sphere(prevent_seam=True)
        
        # Orient Near Side (0° Longitude) towards front camera angle
        self.mesh.rotate_z(-90)
        return self.mesh

    def load_texture(self, mode="standard"):
        """
        Load texture image based on selected mode
        """
        file_path = self.topography_path if mode == "topography" else self.texture_path

        if os.path.exists(file_path):
            try:
                texture = pv.read_texture(file_path)
                print(f"Loaded '{mode}' mode texture successfully!")
                return texture
            except Exception as e:
                print(f"Error loading texture ({mode}): {e}")
                return None
        else:
            print(f"Warning: File not found at '{file_path}'")
            return None

    def setup_sun_lighting(self, plotter):
        """
        Setup Front-facing Sun Light matching NASA/Web Globe viewer illumination.
        """
        plotter.remove_all_lights()

        # Front Sunlight (ප්‍රධාන සූර්යාලෝකය)
        sun_light = pv.Light(
            position=(150.0, -600.0, 300.0),
            focal_point=(0.0, 0.0, 0.0),
            color='white',
            intensity=1.5
        )

        # Ambient Fill Light (අඳුරු පැත්තේ එළිය මඳක් වැඩි කරන ලදී: 0.05 -> 0.12)
        fill_light = pv.Light(
            position=(-300.0, -400.0, 100.0),
            focal_point=(0.0, 0.0, 0.0),
            color='#d0d0e0',
            intensity=0.12
        )

        plotter.add_light(sun_light)
        plotter.add_light(fill_light)

    def add_to_plotter(self, plotter, mode="standard"):
        """
        Render 3D Moon into PyVista Plotter scene.
        """
        if self.mesh is None:
            self.build_mesh()

        texture = self.load_texture(mode=mode)
        self.setup_sun_lighting(plotter)

        if texture:
            self.actor = plotter.add_mesh(
                self.mesh, 
                texture=texture, 
                smooth_shading=True,
                ambient=0.15,        # පරිසර ආලෝකය මඳක් වැඩි කරන ලදී: 0.08 -> 0.15
                diffuse=0.85,        
                specular=0.05,       
                roughness=0.8
            )
        else:
            self.actor = plotter.add_mesh(
                self.mesh, 
                color='#808080', 
                smooth_shading=True,
                ambient=0.15
            )
        return self.actor


if __name__ == "__main__":
    test_plotter = pv.Plotter()
    test_plotter.set_background('black')
    
    moon = MoonModel(radius=100.0)
    moon.add_to_plotter(test_plotter, mode="standard")
    
    print("Testing Solar Lighting Moon setup...")
    test_plotter.show()