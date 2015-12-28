import numpy

def gravitation(r, mu):
    """Returns acceleration due to gravity"""

    # mu = G * M
    g = - mu / numpy.linalg.norm(r) / numpy.linalg.norm(r)
    a = g*r/numpy.linalg.norm(r)

    return a

