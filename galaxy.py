import numpy as np

import vpython as vp
from vpython import vector as v
from vpython import rotate as rot

# gravitacion
g_constant = 6.67408e-11
sagittarius_a_mass = 4e6 # 4e4 to 4e9 
sun_mass = 1.989e30
distances_scale = 1e16

def generateParticles(count=2000):
    golden = (1.0 + np.sqrt(5)) / 2.0

    radius_i, radius_f = 2.0, 100.0
    scatter_xy_i, scatter_xy_f = 0.1, 10.0
    scatter_z_i, scatter_z_f = 1.3, 0.1

    radiuses = np.linspace(radius_i, radius_f, count)
    angles = (np.pi / (2 * np.log(golden))) * np.log(radiuses)

    # dispersar particulas
    scatter_xy_factor = np.linspace(scatter_xy_i, scatter_xy_f, count)
    scatter_x = np.random.normal(-1, 1, count) * scatter_xy_factor
    scatter_y = np.random.normal(-1, 1, count) * scatter_xy_factor
    scatter_z = np.random.normal(-1, 1, count) * \
        np.linspace(scatter_z_i, scatter_z_f, count)

    # convert to cartesian
    x = radiuses * np.cos(angles) + scatter_x
    y = radiuses * np.sin(angles) + scatter_y
    z = scatter_z

    vectors = [v(x[i], y[i], z[i]) for i in range(count)]

    # VY Canis Majoris & OGLE-TR-122A en masas solares
    canis_mass, ogle_mass = 17 * sun_mass, 0.98 * sun_mass

    masses = np.random.uniform(ogle_mass, canis_mass, count)
    # porcentage de masa que representan los cuerpos no visibles en relacion a la estrella
    perc = np.linspace(1, 1.2, count)
    masses = masses * perc

    return vectors, masses


def calculateInitialSpeed(positions, masses):
    up = v(0.0, 0.0, 1.0)
    initialSpeed = [np.sqrt(g_constant * sagittarius_a_mass * masses[i] / (positions[i].mag))
                    * positions[i].cross(up).norm() for i in range(len(positions))]

    # add some randomness
    for s in initialSpeed:
        s.x = s.x + (np.random.rand() * 2.0 - 1.0) * 5.0
        s.y = s.y + (np.random.rand() * 2.0 - 1.0) * 5.0

    return initialSpeed


# configure scene
mainCanvas = vp.canvas(width=1800, height=900, background=vp.color.black)
mainCanvas.camera.autoscale = False
mainCanvas.camera.autocenter = False
sCenter = vp.sphere(pos=v(0, 0, 0), radius=1, color=vp.color.red)

count = 2000
positions, masses = generateParticles(count)
speeds = calculateInitialSpeed(positions, masses)

particles = [vp.sphere(pos=positions[i], radius=0.1, color=vp.color.white,
                       make_trail=False, retain=10) for i in range(count)]

rate = 100
delta_tiempo = 1e-13
while True:
    vp.rate(rate)

    for i in range(count):
        # centripetal acceleration
        acceleration = (g_constant * sagittarius_a_mass *
                        masses[i] / (positions[i].mag2)) * -positions[i].norm()

        # update speed an position
        speeds[i] += acceleration * delta_tiempo
        positions[i] = positions[i] + speeds[i] * delta_tiempo
        particles[i].pos = positions[i]
