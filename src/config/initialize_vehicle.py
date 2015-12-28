import numpy

def initialize_vehicle():

    # These are parameters that should be in a config file
    r = numpy.array([6778000.0, 0.0])
    v = numpy.array([0.0, 8000.0])
    a = numpy.array([0.0, 0.0])

    return r, v, a

