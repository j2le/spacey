import numpy
import math
import atmosphere
from rv2oe import rv2oe
from rk4 import rk4

class vehicle(object):
    def __init__(self, init_scenario):
        self.isp = 300.0
        self.thrusting = 0
        self.dry_mass = 1000.0
        self.dv_propellant_mass = 1000.0
        self.attitude_propellant_mass = 10.0
        self.thrust = 20000.0
        self.day = 0
        self.delta_attitude = 0.0
        if (init_scenario == "leo"):
            self.r = numpy.array([6778000.0, 0.0])
            self.v = numpy.array([0.0, 8000.0])
            self.a = numpy.array([0.0, 0.0])
            self.a_mag = 0.0
            self.r_parent = self.r
            self.v_parent = self.v
            self.parent_body = "earth"
            self.attitude = 0.0
        elif (init_scenario == "entry"):
            self.r = numpy.array([6678000.0, 0.0])
            self.v = numpy.array([-100.0, 7500.0])
            self.a = numpy.array([0.0, 0.0])
            self.a_mag = 0.0
            self.r_parent = self.r
            self.v_parent = self.v
            self.parent_body = "earth"
            self.attitude = 0.0
        elif (init_scenario == "launch"):
            self.r = numpy.array([6378000.0, 0.0])
            self.v = numpy.array([0.0, 0.0])
            self.a = numpy.array([0.0, 0.0])
            self.a_mag = 0.0
            self.r_parent = self.r
            self.v_parent = self.v
            self.parent_body = "earth"
            self.attitude = 90.0
        self.vr_parent = self.v_parent
        self.r_display = numpy.array([0.0, 0.0])
        self.longitude = 0
        self.horizontal_position = 0
        self.v_display_init = numpy.array([0.0, 8000.0])
        self.dv_ideal = 0
        self.q_aero = 0
        self.fin_delta_attitude = 0
        self.fin_angle = 0

    def update(self,sim,parent_mu,parent_radius,time,parent_omega):

        # update vehicle atitude
        self.attitude = self.attitude + self.delta_attitude

        # reentry dynamics
        # if dyanmic pressure is greater than x go to trim angle of attack 
        if (self.q_aero > 1000 and not(self.thrusting)):
            self.fin_delta_attitude = self.fin_delta_attitude +  self.delta_attitude
            if (self.fin_delta_attitude > 90): 
                self.fin_delta_attitude = 90
            elif (self.fin_delta_attitude < 0):
                self.fin_delta_attitude = 0
            self.attitude = 90 - math.atan2(self.v_parent[1],self.v_parent[0]) * 180/math.pi + self.fin_delta_attitude

        # reset q_aero
        if (self.q_aero < 1000):
            self.fin_delta_attitude = 45
        
        # Update forces
        if (self.thrusting):

          # thrust is in Newtons and vehicle mass is in kg
          self.a_mag = self.thrust/(self.dry_mass + self.dv_propellant_mass + self.attitude_propellant_mass)
          self.dv_ideal = self.dv_ideal + self.a_mag * sim.dt
          dprop = sim.dt * (self.thrust / self.isp)

          # give infinite propellant
          if (self.dv_propellant_mass > 0):
              self.dv_propellant_mass = self.dv_propellant_mass - dprop
        else:
          self.a_mag = 0

        self.a[0] = self.a_mag * math.sin(self.attitude*math.pi/180)
        self.a[1] = self.a_mag * math.cos(self.attitude*math.pi/180)

        # update aerodynamic forces
        rho = 0
        if (numpy.linalg.norm(self.r_parent) - parent_radius > 200000):
            rho = 0
        elif (numpy.linalg.norm(self.r_parent) - parent_radius < 0):
            rho = atmosphere.get_density(0)
        else: 
            rho = atmosphere.get_density(numpy.linalg.norm(self.r_parent) - parent_radius) 

        # compute aerodynamic drag
        self.q_aero = 0.5 * rho * numpy.linalg.norm(self.v_parent) * numpy.linalg.norm(self.v_parent)
        drag_aero = 0.1 * 10 * self.q_aero 
        lift_aero = 0.1 * 10 * self.q_aero * math.sin(self.fin_delta_attitude*math.pi/180) 
        a_drag_aero = drag_aero/(self.dry_mass + self.dv_propellant_mass + self.attitude_propellant_mass)
        a_lift_aero = lift_aero/(self.dry_mass + self.dv_propellant_mass + self.attitude_propellant_mass)
        if (numpy.linalg.norm(self.v_parent) > 5e-14):
            self.a[0] = self.a[0] - a_drag_aero*self.v_parent[0]/numpy.linalg.norm(self.v_parent) 
            self.a[1] = self.a[1] - a_drag_aero*self.v_parent[1]/numpy.linalg.norm(self.v_parent) 
            self.a[0] = self.a[0] + a_lift_aero*self.v_parent[1]/numpy.linalg.norm(self.v_parent) 
            self.a[1] = self.a[1] - a_lift_aero*self.v_parent[0]/numpy.linalg.norm(self.v_parent) 
        self.a_mag = numpy.linalg.norm(self.a) 

        # propagate the vehicle state
        prev_r = self.r_parent
        prev_v = self.v_parent
        state = rk4(self.r_parent, self.v_parent, self.a, sim.dt, parent_mu)
        self.r_parent = state[0]
        self.v_parent = state[1]

        # compute planet relative velocity and position
        self.vr_parent[0] = self.v_parent[0] - parent_omega * self.r_parent[1] 
        self.vr_parent[1] = self.v_parent[1] + parent_omega * self.r_parent[0] 

        self.altitude = numpy.linalg.norm(self.r_parent) - parent_radius
        if (self.altitude <=0 and not(self.thrusting)):
            self.r_parent[0] = parent_radius * self.r_parent[0] / numpy.linalg.norm(self.r_parent) 
            self.r_parent[1] = parent_radius * self.r_parent[1] / numpy.linalg.norm(self.r_parent) 
            self.v_parent = numpy.array([0.0, 0.0])

        self.longitude = math.atan2(self.r_parent[1],self.r_parent[0]) + parent_omega * time
        self.horizontal_position = self.longitude*parent_radius

        # compute the orbital elements
        # this should be vehicle.state.compute_orbital_elements
        self.oe = rv2oe(self.r_parent, self.v_parent, parent_mu)
        self.ra = self.oe[2]
        self.rp = self.oe[3]
        self.altitude = numpy.linalg.norm(self.r_parent) - parent_radius
        self.perigee = self.rp - parent_radius
        self.apogee = self.ra - parent_radius
        self.semjax = self.oe[0]
        self.semrax = self.oe[5]
        self.argp = self.oe[4]*180/math.pi
        self.period = self.oe[6]



