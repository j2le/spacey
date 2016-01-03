import numpy
import atmosphere
from rk4 import rk4 
import math

class flight_computer(object):
    def __init__(self):
        self.traj_display_dt_max = 2000

    def update(self,vehicle,display,parent):

        self.traj_display_dt_max = 2000

        # update guidance algorithm
        [display.r_trajectory, display.v_trajectory, display.r_iip_final, display.v_iip_final] = self.update_guidance(
                             vehicle.dry_mass + vehicle.dv_propellant_mass + vehicle.attitude_propellant_mass,
                             vehicle.r, vehicle.v, vehicle.period, vehicle.perigee, vehicle.altitude,
                             display.scale, display.center_x, display.center_y, display.viewing_angle,
                             parent.radius, parent.mu, parent.g0)

    # guidance algorithm for plotting points
    def update_guidance(self, mass, r, v, period, perigee, altitude, scale, center_x, center_y, viewing_angle, radius, mu, g0):

        # determine dt based on a period
        points = 200
        v_mag = numpy.linalg.norm(v) 
        fpa = math.atan2(v[1],v[0])
        dt = period/points
        if (dt < 0.01):
           dt = 0.01
        if dt > self.traj_display_dt_max:
           dt = self.traj_display_dt_max
        r_list = list()
        v_list = list()
        a = numpy.array([0, 0])
        r_display = numpy.array([0, 0])
        append_to_list = True
        fpa_prev = math.atan2(v[1],v[0])
        dt_small = 0.0001
        dt_prev = 0.0001

        for i in range(points):

           # check to see if you should use parent or sibling for propagation
           parent_R = math.sqrt(r[0]**2 + r[1]**2)

           R = math.sqrt(r[0]**2 + r[1]**2)

           # update aerodynamic forces
           a = numpy.array([0,0])
           if (R - radius > 200000):
               rho = 0
           elif (R - radius < 0):
               rho = atmosphere.get_density(0)
               dt = 3
           else:
               rho = atmosphere.get_density(R - radius)
               dt = 3

           # compute aerodynamic drag
           q_aero = 0.5 * rho * numpy.linalg.norm(v) * numpy.linalg.norm(v)
           drag_aero = 0.1 * 10 * q_aero
           lift_aero = 0.1 * 10 * q_aero * math.sin(0/180)
           a_drag_aero = drag_aero/(mass)
           a_lift_aero = lift_aero/(mass)
           if (numpy.linalg.norm(v) > 5e-14):
               a[0] = a[0] - a_drag_aero*v[0]/numpy.linalg.norm(v)
               a[1] = a[1] - a_drag_aero*v[1]/numpy.linalg.norm(v)
               a[0] = a[0] + a_lift_aero*v[1]/numpy.linalg.norm(v)
               a[1] = a[1] - a_lift_aero*v[0]/numpy.linalg.norm(v)
               a_mag = numpy.linalg.norm(a)

           if (append_to_list):
               r_display[0] = r[0]*math.cos(viewing_angle) - r[1]*math.sin(viewing_angle)
               r_display[1] = r[0]*math.sin(viewing_angle) + r[1]*math.cos(viewing_angle)
               r_list.append((r_display[0]/scale+center_x,r_display[1]/scale+center_y))
               if (i <= 2):
                   v_list.append((r_display[0]/scale+center_x,r_display[1]/scale+center_y))
           # stop appending
           if (R < radius and i > 0):
              append_to_list = False
           v_mag = numpy.linalg.norm(v)
           r_mag = numpy.linalg.norm(r)
           angle_rate_max = 1000*math.pi/180
           fpa = math.atan2(v[1],v[0])
           if (i == 0):
               fpa_rate = abs(fpa - fpa_prev)/dt_small
           else:
               fpa_rate = abs(fpa - fpa_prev)/dt

           if (i == 0):
              state = rk4(r, v, a, dt_small, mu)
           elif (fpa_rate > angle_rate_max):
              state = rk4(r, v, a, dt*angle_rate_max/fpa_rate, mu)
           else:
              state = rk4(r, v, a, dt, mu)

           fpa_prev = fpa
           r = state[0]
           v = state[1]

        return r_list, v_list, r, v

