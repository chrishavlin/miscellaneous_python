import numpy as np 
from numpy import typing as npt 
from vispy.scene.visuals import Mesh
import numba 


@numba.njit  
def _generate_ellipsoid_faces_verts(
        phi_cell_centers: npt.NDArray,
        dphi: float,         
        theta_cell_centers: npt.NDArray, 
        dtheta: float, 
        axes_scales: npt.NDArray, 

) -> tuple[npt.NDArray, npt.NDArray]:
    '''
    returns verts, faces 
    verts: vertex coordinates in spherical coordinates with ordering (r, theta, phi) 
    faces: face-triangle index mapping to vertex indices.    
    '''
    verts = []
    faces = []

    dphi2 = dphi / 2. 
    dtheta2 = dtheta / 2. 

    n_theta = len(theta_cell_centers)
    n_phi = len(phi_cell_centers)    

    # ellipsoid axes
    asq = axes_scales[0] ** 2
    bsq = axes_scales[1] ** 2
    csq = axes_scales[2] ** 2

    n_phi_edgees = n_phi + 1 
    n_verts = 0

    # this single nested loop generates both the 
    # individual vertices and the connectivity (the
    # faces)
    for itheta in range(0, n_theta+1):
        for iphi in range(0, n_phi+1):
        
            # get the new verts   
            if itheta == n_theta:
                theta = theta_cell_centers[itheta-1] + dtheta2
            else:         
                theta = theta_cell_centers[itheta] - dtheta2
            
            if iphi == n_phi:
                phi = phi_cell_centers[iphi-1] + dphi2
            else:
                phi = phi_cell_centers[iphi] - dphi2
            
            # calculate r for this vert             
            cos2th = np.cos(theta) ** 2
            cos2phi = np.cos(phi) ** 2
            sin2th = np.sin(theta) ** 2
            sin2phi = np.sin(phi) ** 2

            val = sin2th * cos2phi / asq 
            val += sin2th * sin2phi / bsq
            val += cos2th / csq
            r = np.sqrt(1./val)

            # maybe move the coordinate conversion here because 
            # why not?

            # add this one vert
            verts.append([r, theta, phi])
            n_verts+=1            

            # now for some triangles: note that some of the 
            # faces here will reference index values that dont
            # yet existing in the verts array but thats OK as 
            # they will existing by the end of this nested loop.
            if itheta < n_theta and iphi < n_phi:

                # get the 4 indices for the corners of this 
                # face, build 2 triangles to cover it. 
                iface_ij = itheta * n_phi_edgees + iphi                
                iface_phi_p1 = iface_ij + 1
                iface_theta_phi_p1 = iface_phi_p1 + n_phi_edgees
                iface_theta_p1 = iface_ij + n_phi_edgees          
                
                faces.append([iface_ij, iface_phi_p1, iface_theta_phi_p1])
                faces.append([iface_ij, iface_theta_phi_p1, iface_theta_p1])                
    
    return np.array(verts, dtype=np.float64), np.array(faces, dtype=np.int64)


def _sphere_to_cart(r: npt.NDArray, theta: npt.NDArray, phi: npt.NDArray) -> tuple[npt.NDArray, : npt.NDArray, : npt.NDArray]:
    z = r * np.cos(theta)
    xy = r * np.sin(theta)
    x = xy * np.cos(phi)
    y = xy * np.sin(phi)
    return x, y, z


class PartialEllipsoid:
    def __init__(self, 
                 axes_scales: npt.ArrayLike,
                 center: npt.ArrayLike | None = None,
                 phi_range: npt.ArrayLike | None = None, 
                 theta_range: npt.ArrayLike | None = None, 
                 ):
        
        """
        a 3D, axis-aligned partial ellipsoid 

        Parameters
        ----------
        axes_scales: 
            the x, y, z ellipsoid axis scales 
        center: 
            the center of the ellipsoid (default is (0., 0., 0.))
        phi_range: 
            min and max azimuthal (longitudinal) values in radians
        theta_range: 
            min and max co-latitude values in radians

        """
        
        self.axes_scales = np.asarray(axes_scales)
        assert(len(self.axes_scales) == 3)

        if center is None:
            center = np.zeros((3,))            
        self.center = np.asarray(center)
        assert(len(self.center) == 3)

        if phi_range is None:
            phi_range = np.array([0, 2 * np.pi])
        self.phi_range = np.asarray(phi_range)
        assert(len(self.phi_range) == 2)

        if theta_range is None:
            theta_range = np.array([0, np.pi])
        self.theta_range = np.asarray(theta_range)
        assert(len(self.theta_range) == 2)

        self.verts: npt.NDArray = None
        self.faces: npt.NDArray = None
        self.mesh: Mesh = None

    def generate_verts_and_faces(self, 
                                 n_phi: int = 32, 
                                 n_theta: int = 16) -> tuple[npt.NDArray, npt.NDArray]:
        '''
        n_phi: number of azimuthal (longitudinal) face-cells
        n_theta: number of co-latitude face-cells 
        
        '''
        phi_edges = np.linspace(self.phi_range[0], self.phi_range[1], n_phi+1)
        th_edges = np.linspace(self.theta_range[0], self.theta_range[1], n_theta+1)
        phi_c = (phi_edges[:-1]  + phi_edges[1:]) / 2
        th_c = (th_edges[:-1]  + th_edges[1:]) / 2
        dphi = np.mean(phi_edges[1:] - phi_edges[:-1])
        dtheta = np.mean(th_edges[1:] - th_edges[:-1])
        
        verts, faces = _generate_ellipsoid_faces_verts(
            phi_c, 
            dphi, 
            th_c, 
            dtheta,
            self.axes_scales
        )

        verts_x, verts_y, verts_z = _sphere_to_cart(verts[:,0], verts[:,1], verts[:,2])

        # shift it all to the center 
        verts_x += self.center[0]
        verts_y += self.center[1]
        verts_z += self.center[2]
                
        verts = np.column_stack([verts_x, verts_y, verts_z])        
        assert verts.shape[1] == 3

        self.verts = verts
        self.faces = faces
        return self.verts, self.faces

    def generate_mesh(self, n_phi=None, n_theta=None, **kwargs) -> Mesh:
        """
        Generate the vispy Mesh

        n_phi, n_theta ignored if verts and faces already exists: call 
        generate_verts_and_faces again to re-generate. 

        kwargs are forwarded to vispy.scene.visuals.Mesh

        """
        if self.verts is None:
            _ = self.generate_verts_and_faces(n_phi=n_phi, n_theta=n_theta)
        self.mesh = Mesh(self.verts, self.faces, **kwargs)
        return self.mesh

