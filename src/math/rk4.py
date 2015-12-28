from gravitation import gravitation
import math
import numpy

def rk4(r, v, a, dt, mu):
    """Returns final (position, velocity) tuple after
    time dt has passed.

    r: initial position (number-like object)
    v: initial velocity (number-like object)
    a: acceleration function a(r,v,dt) (must be callable)
    dt: timestep (number)"""
    r1 = r
    v1 = v
    a1 = a + gravitation(r1, mu)

    r2 = r + 0.5*v1*dt
    v2 = v + 0.5*a1*dt
    a2 = a + gravitation(r2, mu)

    r3 = r + 0.5*v2*dt
    v3 = v + 0.5*a2*dt
    a3 = a + gravitation(r3, mu)

    r4 = r + v3*dt
    v4 = v + a3*dt
    a4 = a + gravitation(r4, mu)

    rf = r + (dt/6.0)*(v1 + 2*v2 + 2*v3 + v4)
    vf = v + (dt/6.0)*(a1 + 2*a2 + 2*a3 + a4)

    return rf, vf

