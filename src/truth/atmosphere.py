import numpy
import math

def get_density(altitude):

    # http://en.wikipedia.org/wiki/Scale_height
    # rho is in kg/m^3 and altitude is density in m
    rho_0 = 1.2
    rho = rho_0*math.exp(-altitude/7000)

    return rho

