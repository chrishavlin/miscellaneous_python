from vispy import app, scene
from vispy.visuals.filters import WireframeFilter
from vispy_helper import PartialEllipsoid
import numpy as np 
import sys 

if __name__ == "__main__":
    # Create canvas and view
    canvas = scene.SceneCanvas(keys='interactive', size=(600, 600), show=True)
    view = canvas.central_widget.add_view()
    view.camera = scene.cameras.ArcballCamera(fov=0)


    if len(sys.argv) > 1: 
        ellipse_option = str(sys.argv[1])
    else:
        ellipse_option = 'ellipse'

    if ellipse_option == 'sphere':
        # sphere
        scales = (1., 1., 1.)  
        phi_range = (0., 2 * np.pi)  # azimuth
        theta_range = (0, np.pi) # co-latitude in radians 
    elif ellipse_option == 'ellipse':
        # a full ellipse
        scales = (1.5, 1., .75)  
        phi_range = (0., 2 * np.pi)  # azimuth
        theta_range = (0, np.pi) # co-latitude in radians
    elif ellipse_option == 'ellipse_hemi':
        # nice ellipse half
        scales = (2., 1.5, 1.)  
        phi_range = (0., np.pi * 2)  # azimuth
        theta_range = (np.pi/2, np.pi) # co-latitude in radians 
    elif ellipse_option == 'quadrant':
        # ellipse quadrant
        scales = (2., 1.5, 1.)  
        phi_range = (0., np.pi *3/4)  # azimuth
        theta_range = (np.pi/4, np.pi/2+np.pi/4) # co-latitude in radians 


    pe = PartialEllipsoid(scales, 
                        phi_range=phi_range, 
                        theta_range=theta_range, 
                        )

    verts, faces = pe.generate_verts_and_faces(n_phi=64, n_theta=32)

    mesh = pe.generate_mesh(color=(1., 0., 0., 0.5)) # the vispy Mesh!
    view.add(mesh)

    # Use filters to affect the rendering of the mesh.
    # see https://vispy.org/gallery/scene/mesh_shading.html
    # for changing properties of mesh view
    wireframe_filter = WireframeFilter(width=0.5, color=(0., 0., 0., 0.1))
    mesh.attach(wireframe_filter)

    canvas.show()

    app.run()


