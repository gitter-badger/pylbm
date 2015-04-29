import pyLBM
from pyLBM.viewer import VtkViewer
import math
import numpy as np
import sympy as sp
from sympy.matrices import Matrix, zeros
from pyevtk.hl import imageToVTK


X, Y, Z, LA = sp.symbols('X,Y,Z,LA')

u = [[sp.Symbol("m[%d][%d]"%(i,j)) for j in xrange(25)] for i in xrange(10)]

def initialization_rho(x, y, z):
    return np.ones((x.shape[0], y.shape[0], z.shape[0]))

def initialization_q(x, y, z):
    return np.zeros((x.shape[0], y.shape[0], z.shape[0]))

def bc_up(f, m, x, y, z, scheme):
    m[:, 3] = -math.sqrt(2)/20.
    m[:, 5] = -math.sqrt(2)/20.
    m[:, 7] = 0.
    scheme.equilibrium(m)
    scheme.m2f(m, f)

def plot(sol, num):
    sol.time_info()
    print "Build image {0:3d}".format(num)
    sol.f2m()
    print "t = {0}, |qx| <= {1:10.3e}".format(sol.t, np.linalg.norm(sol.m[0][3][1:-1,1:-1,1:-1].reshape((nx*ny*nz,)), np.inf))
    sol.save[:] = np.sqrt(sol.m[0][3][1:-1,1:-1,1:-1]**2 +
                  sol.m[0][5][1:-1,1:-1,1:-1]**2 +
                  sol.m[0][7][1:-1,1:-1,1:-1]**2)
    imageToVTK("./data/image_{0}".format(num), pointData = {"q**2" : sol.save} )

dx = 1./128
la = 1.
rho0 = 1.
Re = 200
nu = 5./Re

s1 = 1.6
s2 = 1.2
s4 = 1.6
s9 = 1./(3*nu +.5)
s11 = s9
s14 = 1.2

r = X**2+Y**2+Z**2

dico = {
    'box':{'x':[0., 1.], 'y':[0., 1.], 'z':[0., 1.], 'label':[0, 0, 0, 0, 0, 1]},
    'space_step':dx,
    'scheme_velocity':la,
    'schemes':[{'velocities':range(7) + range(19,27),
               #'velocities':[0, 5, 6, 3, 4, 1, 2, 19, 23, 21, 25, 20, 24, 22, 26],
               'polynomials':Matrix([1,
                             r - 2, .5*(15*r**2-55*r+32),
                             X, .5*(5*r-13)*X,
                             Y, .5*(5*r-13)*Y,
                             Z, .5*(5*r-13)*Z,
                             3*X**2-r, Y**2-Z**2,
                             X*Y, Y*Z, Z*X,
                             X*Y*Z]),
                'relaxation_parameters':[0, s1, s2, 0, s4, 0, s4, 0, s4, s9, s9, s11, s11, s11, s14],
                'equilibrium':Matrix([u[0][0],
                                  -u[0][0] + u[0][3]**2 + u[0][5]**2 + u[0][7]**2,
                                  -u[0][0],
                                  u[0][3],
                                  -7./3*u[0][3],
                                  u[0][5],
                                  -7./3*u[0][5],
                                  u[0][7],
                                  -7./3*u[0][7],
                                  1./3*(2*u[0][3]**2-(u[0][5]**2+u[0][7]**2)),
                                  u[0][5]**2-u[0][7]**2,
                                  u[0][3]*u[0][5],
                                  u[0][5]*u[0][7],
                                  u[0][7]*u[0][3],
                                  0]),
                'init':{0:(initialization_rho,),
                        3:(initialization_q,),
                        5:(initialization_q,),
                        7:(initialization_q,)
                        },
                }],
        'boundary_conditions':{
                    0:{'method':{0: pyLBM.bc.bouzidi_bounce_back}, 'value':None},
                    1:{'method':{0: pyLBM.bc.bouzidi_bounce_back}, 'value':bc_up},
                    },
        'generator': pyLBM.generator.CythonGenerator,

    }

## verification
# geom = pyLBM.Geometry(dico)
# geom.visualize(viewlabel=True)
# sten = pyLBM.Stencil(dico)
# print sten
# v = VtkViewer()
# sten.visualize(v)
# dom = pyLBM.Domain(dico)
# dom.visualize(opt=1)
# print dom


sol = pyLBM.Simulation(dico)
nx, ny, nz = sol.domain.Ng
sol.save = np.empty((nx, ny, nz))

im = 0
compt = 0
plot(sol,im)

while sol.t<5.:
    sol.one_time_step()
    compt += 1
    if compt == 16:
        im += 1
        compt = 0
        plot(sol,im)

sol.time_info()