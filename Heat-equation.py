# Script to generate heat map with randomly moving heat source.
# modified from online code
# Yun Long, 04/26/2018
# Hope we can get NIPS accepted

import numpy as np
import matplotlib.pyplot as plt

# plate size, mm, rectangle shape
w = h = 6.4
# heat source size, round shape
r = 0.5
# intervals in x-, y- directions, mm, heat map size 100x100
dx = dy = 0.1
dx2 = dy2 = 0.01
# Thermal diffusivity/conductivity of steel, mm2.s-1
D = 0.2
C = 20
# heat source start location
lx = 1
ly = 1
# heat source moving direction (speed is a constant 1)
vx = np.random.rand() * 8
vy = np.sqrt(64 - vx * vx)
# Initial temperature for the plate and heat source
Tcool, Thot = 300, 700

# number of grids at x, y directions
nx, ny = int(w/dx), int(h/dy)

# time step (s)
dt = 0.001

t0 = Tcool * np.ones((nx, ny))
t1 = Tcool * np.ones((nx, ny))

# set the boundary always at the low temperature
def set_boundary():
    global t1, t0
    t0[:,ny-1] = Tcool
    t0[:,0] = Tcool
    t0[0,:] = Tcool
    t0[nx-1,:] = Tcool


# heat convection from heat source to the 2-D plate
def convection():
    global t1, t0
    for i in range(nx):
        for j in range(ny):
            distance = (i*dx-lx)**2 + (j*dy-ly)**2
            if distance < r:
                t1[i,j] = (Thot - t0[i,j]) * C * dt + t0[i,j]

# heat transfer to neighbor
def transfer():
    global t1, t0
    t1[1:-1, 1:-1] = t0[1:-1, 1:-1] + D * dt * (
            (t0[2:, 1:-1] - 2 * t0[1:-1, 1:-1] + t0[:-2, 1:-1]) / dx2
            + (t0[1:-1, 2:] - 2 * t0[1:-1, 1:-1] + t0[1:-1, :-2]) / dy2)

# update the location of heat source
def update_location():
    global lx,ly
    lx = lx + vx * dt
    ly = ly + vy * dt

# number of steps
N = 501
iter = 0
records = np.ones((nx,ny,10))

for i in range(N):
    convection()
    transfer()
    update_location()
    set_boundary()
    t0 = t1
    if (i+1) % 50 == 0:
        records[:,:,iter] = t0
        iter = iter +1

fig = plt.figure()
for i in range(1,11):
    plt.subplot(2, 5, i)
    plt.imshow(records[:,:,i-1], cmap='hot', interpolation='nearest',vmin=Tcool,vmax=Thot)
plt.show()




