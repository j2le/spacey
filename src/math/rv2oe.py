# computes orbital elements from position and velocity
import numpy 
import math

def rv2oe(r, v, mu):
    # perigee radius
    # apogee radius

    # compute the radius and velocity unit vectors
    r_unit = r / numpy.linalg.norm(r)
    semjax = 1/(2/numpy.linalg.norm(r) - numpy.linalg.norm(v)**2 / mu)

    # compute the eccentricity vectory
    # http://en.wikipedia.org/wiki/Eccentricity_vector
    if (numpy.linalg.norm(v) > 0):
       e = numpy.linalg.norm(v)*numpy.linalg.norm(v)*r/mu - numpy.dot(r,v)*v/mu  - r_unit
    else:
       e = [0, 0]

    # compute the eccentricity magnitude
    e_mag = numpy.linalg.norm( e )

    # compute the apogee and perigee radius
    rp = semjax*(1-e_mag)
    ra = semjax*(1+e_mag)

    # compute the argument of perigee
    argp = math.atan2(e[0], e[1])

    # compute the semi-minor axis
    if e_mag < 1:
        semrax = semjax*math.sqrt(1-e_mag**2)
    else:
        semrax = 0

    # compute the period of the orbit
    # @todo provide rationale for returning 200000 when eccentricity is greater than 1.
    if e_mag < 1:
        period = 2*math.pi*math.sqrt(semjax**3/mu)
    else:
        period = 200000

    #return semjax, e, ra, rp
    return semjax, e, ra, rp, argp, semrax, period

