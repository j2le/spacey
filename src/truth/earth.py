import numpy
import math

class earth(object):
    def __init__(self):

        self.angle = 0.0

        # http://en.wikipedia.org/wiki/Standard_gravitational_parameter
        # m^3/s^2
        self.mu = 398600.4418*1000*1000*1000

        # Earth radius (m)
        self.radius = 6378000

        # Earth rotaiton rate (rad/s)
        #self.omega = 7.291e-5
        # @todo why is this zero?
        self.omega = 0.0

        # Earth graviation at surface of Earth (m/s^2)
        self.g0 = 9.81

        # sphere of influence of the earth (m)
        self.r_soi =     925000000.0

        # height of atmosphere, above this altitude atmosphere density is zero (m)
        self.atmosphere_height =     1000000.0

        # set position in the inertial frame (m)
        self.r = numpy.array([0, 0])
        self.v = numpy.array([0, 0])

    def update(self,sim):

      # update rotation for earth
      self.r = numpy.array([0, 0])
      self.v = numpy.array([0, 0])
      self.angle =   self.angle + sim.dt * self.omega
      if (self.angle > 2*math.pi):
         self.angle = self.angle - 2*math.pi

